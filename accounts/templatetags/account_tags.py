from django import template

register = template.Library()

@register.filter
def display_role(role):
    roles = {
        'fleet_manager': 'Fleet Manager',
        'dispatcher': 'Dispatcher',
        'safety_officer': 'Safety Officer',
        'financial_analyst': 'Financial Analyst',
    }
    return roles.get(role, role.replace('_', ' ').title() if role else '')
