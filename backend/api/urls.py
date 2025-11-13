from django.urls import path
from .views import ping, init, check_code, my_checker_days, my_support_days, set_support_time, checker_day_detail, propose_support_time, respond_support_proposal, start_inspection, answer_inspection, complete_inspection, month_matrix, available_months, month_matrix_export, analytics_overview

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('init/', init, name='init'),
    path('checker/days/', my_checker_days, name='my_checker_days'),
    path('support/days/', my_support_days, name='my_support_days'),
    path('checker/set_support_time/', set_support_time, name='set_support_time'),
    path('checker/day_detail/', checker_day_detail, name='checker_day_detail'),
    path('checker/propose_support_time/', propose_support_time, name='propose_support_time'),
    path('checker/respond_support_proposal/', respond_support_proposal, name='respond_support_proposal'),
    path('checker/start_inspection/', start_inspection, name='start_inspection'),
    path('checker/answer/', answer_inspection, name='answer_inspection'),
    path('checker/complete_inspection/', complete_inspection, name='complete_inspection'),
    path('check_code/', check_code, name='check_code'),
    path('reports/month_matrix/', month_matrix, name='month_matrix'),
    path('reports/available_months/', available_months, name='available_months'),
    path('reports/month_matrix_export/', month_matrix_export, name='month_matrix_export'),
    path('reports/analytics_overview/', analytics_overview, name='analytics_overview'),
]


