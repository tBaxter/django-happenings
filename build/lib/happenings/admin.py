from django.conf import settings
from django.contrib import admin

from .models import Image, BulkEventImageUpload, UpdateImage
from .models import Event, Update, Memory, ExtraInfo, Schedule
from .forms import AdminAddEventForm

supports_video = False

if 'video' in settings.INSTALLED_APPS:
    from .models import EventVideo
    supports_video = True


class ExtraInfoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class ExtraInfoInline(admin.StackedInline):
    model = ExtraInfo
    extra = 1


class ImageInline(admin.TabularInline):
    model = Image
    extra = 3


class EventBulkInline(admin.TabularInline):
    model = BulkEventImageUpload
    max_num = 1


class UpdateImageInline(admin.TabularInline):
    model = UpdateImage
    max_num = 3
    extra = 1

if supports_video:
    class VideoInline(admin.TabularInline):
        model = EventVideo
        extra = 1


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 3


class EventAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = ('name', 'approved', 'featured', 'submitted_by', 'start_date',)
    list_filter = ('featured', 'region')
    date_hierarchy = 'start_date'
    filter_horizontal = ('attending', 'related_events')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        ImageInline,
        EventBulkInline,
        ExtraInfoInline,
        ScheduleInline,
    ]
    if supports_video:
        inlines.append(VideoInline)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'submitted_by':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return AdminAddEventForm
        else:
            return super(EventAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            fieldsets = (
                ('General info', {
                    'fields': ('submitted_by', 'subhead', 'name', 'info', 'featured')
                }),
                ('Dates', {'fields': (('start_date', 'end_date'))}),
                ('Related', {'fields': ('related_events')}),
                ('Venue/Location', {
                    'fields': (
                        'region',
                        'venue',
                        'address',
                        ('city', 'state', 'zipcode'),
                        ('website', 'phone')
                    )
                }),
                ('Ticketing', {
                    'fields': ('offsite_tickets', 'ticket_sales_end'),
                    'classes': ['collapse']
                }),
                ('Staff info', {
                    'fields': ('admin_notes', 'approved', 'slug'),
                    'classes': ['collapse']
                }),
            )
        else:
            fieldsets = (
                ('General info', {
                    'fields': ('submitted_by', 'subhead', 'name', 'info', 'featured'),
                    'classes': ['collapse']
                }),
                ('Dates', {
                    'fields': (('start_date', 'end_date')),
                    'classes': ['collapse']
                }),
                ('Related', {
                    'fields': ('related_events',),
                    'classes': ['collapse']
                }),
                ('Venue/Location', {
                    'fields': (
                        'region',
                        'venue',
                        'address',
                        ('city', 'state', 'zipcode'),
                        ('website', 'phone')
                    ),
                    'classes': ['collapse']
                }),
                ('Ticketing', {
                    'fields': ('offsite_tickets', 'ticket_sales_end'),
                    'classes': ['collapse']
                }),
                ('Staff info',   {
                    'fields': ('admin_notes', 'approved', 'slug'),
                    'classes': ['collapse']
                }),
                ('Additional info', {'fields': ('recap',)}),

            )
        return fieldsets


class UpdateAdmin(admin.ModelAdmin):
    class Media:
        js = (
            '/static/admin/js/jquery-ui-1.10.3.custom-sortable.min.js',
            '/static/admin/js/inline_reorder.js',
        )

    list_display = ('title', 'pub_time',)
    list_filter = ('event',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        if db_field.name == 'event':
            kwargs['initial'] = Event.objects.filter(featured=True).latest('id')
            return db_field.formfield(**kwargs)
        return super(UpdateAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    inlines = [
        UpdateImageInline,
    ]


class MemoryAdmin(admin.ModelAdmin):
    readonly_fields = ('post_date',)


admin.site.register(Event, EventAdmin)
admin.site.register(Update, UpdateAdmin)
admin.site.register(ExtraInfo, ExtraInfoAdmin)
admin.site.register(Memory, MemoryAdmin)
