from typing import cast
from budgetpet.application.services.monthly_events_service import MonthlyEventsService
from datetime import date, datetime

def should_run_monthly_event(service: MonthlyEventsService) -> None:
    today = datetime.today()
    events = service.get_monthly_events()
    statuses = {}
    
    for event in events:
        if event['is_active'] and event['trigger_day'] == today.day:
            service.update_monthly_event(event['id'], today.date())
            statuses[event['id']] = True
        else:
            statuses[event['id']] = False
    
    service.notify_monthly_events(statuses)

def check_day_of_monthly_events(events: list[dict]) -> list:
    today = date.today()
    events_to_run = []

    for event in events:
        if today.day < event['trigger_day']:
            continue

        last_executed = cast(date, event['last_executed'])
        if last_executed is None:
            events_to_run.append(event['id'])
            continue

        if last_executed.year != today.year or last_executed.month != today.month:
            events_to_run.append(event['id'])
    return events_to_run


def run_monthly_event(events_to_run: list) -> None:
    if 1 in events_to_run:
        pay_rent(1)
    elif 2 in events_to_run:
        monthly_recalculations(2)


def pay_rent(event_id: int) -> None:
    try:
        with db_cursor() as cursor:
            current_balance = get_current_budget_state(cursor)
            updated_state = current_balance.model_copy(update={'rent': Decimal('0')})
            save_budget_state(updated_state, cursor)

            last_executed_update = date.today()
            update_monthly_event(event_id, last_executed_update)
    except Exception as e:
        logger.error('Ошибка при оплате аренды в бюджете: %s', e)


def monthly_recalculations(event_id) -> None:
    try:
        with db_cursor() as cursor:
            current_balance = get_current_budget_state(cursor)

            #Take rent money from 'reserve' and add to 'rent'
            updated_state = current_balance.model_copy(update={"rent": Decimal("810")})
            updated_state.reserve = updated_state.reserve - Decimal("810")

            #Add last month earnings amount to free money (from reserve)
            last_month_income = calculate_last_month_income()
            free_funds = updated_state.available_funds 
            updated_state.available_funds = last_month_income + free_funds
            updated_state.reserve = updated_state.reserve - last_month_income
            save_budget_state(updated_state, cursor)

            last_executed_update = date.today()
            update_monthly_event(event_id, last_executed_update)
    
    except Exception as e:
        logger.debug("Ошибка при ивенте ежемесячных рекалькуляций: %s", e)