from django.contrib import admin
from .models import UserProfile, AccessCode, ROLES, Area, Checklist, ChecklistQuestion, PlanDay, DayAssignment
from django.contrib import admin as django_admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user_id", "last_name", "first_name", "middle_name", "role", "created_at", "updated_at")
    list_filter = ("role", "created_at")
    search_fields = ("user_id", "last_name", "first_name", "middle_name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Пользователь", {"fields": ("user_id",)}),
        ("ФИО", {"fields": ("last_name", "first_name", "middle_name")}),
        ("Доступ", {"fields": ("role",)}),
        ("Метаданные", {"fields": ("created_at", "updated_at")}),
    )
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Ограничиваем результаты автодополнения только пользователями с ролью
        return queryset.exclude(role=""), use_distinct


@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "last_name", "first_name", "middle_name", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("code", "last_name", "first_name", "middle_name")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Код", {"fields": ("code",)}),
        ("ФИО", {"fields": ("last_name", "first_name", "middle_name")}),
        ("Роль", {"fields": ("role",)}),
        ("Метаданные", {"fields": ("created_at",)}),
    )


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "watcher", "created_at")
    search_fields = ("name", "watcher__last_name", "watcher__first_name")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("watcher",)
    fieldsets = (
        ("Участок", {"fields": ("name", "description", "watcher")}),
        ("Метаданные", {"fields": ("created_at",)}),
    )


class ChecklistQuestionInline(admin.TabularInline):
    model = ChecklistQuestion
    extra = 1
    fields = ("order", "text", "reference_image")
    ordering = ("order", "id")


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("title", "area", "created_at", "updated_at")
    list_filter = ("area",)
    search_fields = ("title", "area__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ChecklistQuestionInline]
    fieldsets = (
        ("Чек-лист", {"fields": ("title", "area")}),
        ("Метаданные", {"fields": ("created_at", "updated_at")}),
    )


## Удалены экран и инлайны "План на неделю"


class DayAssignmentInline(admin.TabularInline):
    model = DayAssignment
    extra = 0
    fields = ("area", "responsible")
    autocomplete_fields = ("area", "responsible")
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "responsible":
            from .models import UserProfile
            kwargs["queryset"] = UserProfile.objects.exclude(role="")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PlanDay)
class PlanDayAdmin(admin.ModelAdmin):
    list_display = ("date", "created_at")
    date_hierarchy = "date"
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Расписание на день", {"fields": ("date",)}),
        ("Метаданные", {"fields": ("created_at",)}),
    )
    inlines = [DayAssignmentInline]

# --- Branding ---
django_admin.site.site_header = "Администрационная панель"
django_admin.site.site_title = "Администрационная панель"
django_admin.site.index_title = "Администрационная панель"
