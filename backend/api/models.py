from django.db import models


ROLES = ("admin", "checker", "support")
ROLE_CHOICES = [
    ("admin", "Администратор"),
    ("checker", "Проверяющий"),
    ("support", "Сопровождающий"),
]


class UserProfile(models.Model):
    user_id = models.BigIntegerField("ID пользователя", unique=True, db_index=True)
    last_name = models.CharField("Фамилия", max_length=100, blank=True, default="")
    first_name = models.CharField("Имя", max_length=100, blank=True, default="")
    middle_name = models.CharField("Отчество", max_length=100, blank=True, default="")
    role = models.CharField(
        "Роль",
        max_length=32,
        blank=True,
        default="",
        choices=ROLE_CHOICES,
        help_text="Роль пользователя: Администратор | Проверяющий | Сопровождающий. Пусто — нет доступа.",
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    def __str__(self) -> str:
        return self.full_name or str(self.user_id)

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join([p for p in parts if p]).strip()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

def generate_access_code() -> str:
    import random
    import string

    alphabet = string.ascii_letters + string.digits
    parts = []
    for _ in range(3):
        part = "".join(random.choice(alphabet) for _ in range(4))
        parts.append(part)
    return "-".join(parts)


class AccessCode(models.Model):
    code = models.CharField("Код доступа", max_length=14, unique=True, db_index=True, default=generate_access_code)
    last_name = models.CharField("Фамилия", max_length=100, blank=True, default="")
    first_name = models.CharField("Имя", max_length=100, blank=True, default="")
    middle_name = models.CharField("Отчество", max_length=100, blank=True, default="")
    role = models.CharField(
        "Роль",
        max_length=32,
        choices=ROLE_CHOICES,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    def __str__(self) -> str:
        return f"AccessCode(code={self.code}, role={self.role})"

    class Meta:
        verbose_name = "Код доступа"
        verbose_name_plural = "Коды доступа"

## Удалён прежний неверный Meta на уровне модуля


class Area(models.Model):
    name = models.CharField("Название участка", max_length=200)
    description = models.TextField("Описание", blank=True, default="")
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    watcher = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='watched_areas', verbose_name="Сопровождающий")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"


class Checklist(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="checklists", verbose_name="Участок")
    title = models.CharField("Название чек-листа", max_length=200)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.area.name})"

    class Meta:
        verbose_name = "Чек-лист"
        verbose_name_plural = "Чек-листы"


class ChecklistQuestion(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="questions", verbose_name="Чек-лист")
    text = models.CharField("Текст вопроса", max_length=500)
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    reference_image = models.ImageField("Эталонное фото", upload_to="reference/", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.order}. {self.text}"

    class Meta:
        verbose_name = "Вопрос чек-листа"
        verbose_name_plural = "Вопросы чек-листа"
        ordering = ["order", "id"]

# ---- Планирование ответственности ----
from datetime import timedelta
from django.core.exceptions import ValidationError


class ScheduleWeek(models.Model): ...
class WeekAssignment(models.Model): ...


# --- План на отдельный день ---
class PlanDay(models.Model):
    date = models.DateField("Дата", unique=True, db_index=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    passed = models.BooleanField("Обход выполнен", default=False)
    checked_at = models.DateTimeField("Время обхода", null=True, blank=True)

    class Meta:
        verbose_name = "Расписание на день"
        verbose_name_plural = "Расписания на день"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"План на {self.date}"


class DayAssignment(models.Model):
    plan_day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name="assignments", verbose_name="План дня")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="day_assignments", verbose_name="Участок")
    responsible = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="day_assignments", verbose_name="Ответственный")
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    passed = models.BooleanField("Обход по участку выполнен", default=False)
    checked_at = models.DateTimeField("Время обхода по участку", null=True, blank=True)
    support_time = models.TimeField("Время сопровождающего", null=True, blank=True)

    class Meta:
        verbose_name = "Запись расписания"
        verbose_name_plural = "Записи расписания"
        ordering = ["area_id", "id"]
        constraints = [
            models.UniqueConstraint(fields=["plan_day", "area"], name="unique_area_per_plan_day"),
        ]

    def __str__(self) -> str:
        return f"{self.plan_day.date} — {self.area} — {self.responsible or 'не назначен'}"


class SupportProposal(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидает"),
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
    )
    plan_day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name="support_proposals", verbose_name="План дня")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="support_proposals", verbose_name="Участок")
    proposed_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="made_support_proposals", verbose_name="Инициатор (проверяющий)")
    proposed_time = models.TimeField("Предложенное время")
    status = models.CharField("Статус", max_length=16, choices=STATUS_CHOICES, default="pending", db_index=True)
    decided_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="decided_support_proposals", verbose_name="Кем решено")
    decided_at = models.DateTimeField("Время решения", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Предложение времени"
        verbose_name_plural = "Предложения времени"
        ordering = ["-created_at"]


class InspectionSession(models.Model):
    plan_day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name="inspection_sessions", verbose_name="План дня")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="inspection_sessions", verbose_name="Участок")
    checker = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="inspection_sessions", verbose_name="Проверяющий")
    started_at = models.DateTimeField("Начат", auto_now_add=True)
    completed_at = models.DateTimeField("Завершен", null=True, blank=True)

    class Meta:
        verbose_name = "Сессия обхода"
        verbose_name_plural = "Сессии обхода"
        ordering = ["-started_at"]


class InspectionAnswer(models.Model):
    session = models.ForeignKey(InspectionSession, on_delete=models.CASCADE, related_name="answers", verbose_name="Сессия")
    question = models.ForeignKey(ChecklistQuestion, on_delete=models.CASCADE, related_name="answers", verbose_name="Вопрос")
    passed = models.BooleanField("Соответствует", default=True)
    defect_photo = models.ImageField("Фото дефекта", upload_to="defects/", null=True, blank=True)
    answered_at = models.DateTimeField("Отвечено", auto_now_add=True)

    class Meta:
        verbose_name = "Ответ по обходу"
        verbose_name_plural = "Ответы по обходу"
