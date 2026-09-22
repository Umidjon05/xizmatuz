from .models import Category


def categories_processor(request):
    main_categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    return {'nav_categories': main_categories}
