from django.contrib.admin.sites import AdminSite
from django.utils.text import capfirst
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib import admin

class YawdAdminSite(AdminSite):
    
    def __init__(self, *args, **kwargs):
        super(YawdAdminSite, self).__init__(*args, **kwargs)
        self._registry = admin.site._registry
        self._top_menu = {}
        
    def register_top_menu_item(self, item, icon_class=''):
        app_labels = []
        for model, model_admin in self._registry.iteritems():
            if not model._meta.app_label in app_labels:
                app_labels.append(model._meta.app_label)
        
        if isinstance(item, basestring) and item in app_labels:
            if not item in self._top_menu:
                self._top_menu[item] = icon_class
        else:
            raise Exception("Item has to be a valid app_label")
        
    def unregister_top_menu_item(self, item):
        if isinstance(item, basestring) and item in self._top_menu:
            del self._top_menu[item]
        else:
            raise Exception("Item is not registered in the top menu")
    
    def top_menu(self, request):
        user = request.user
        app_dict = {}

        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            if app_label in self._top_menu:
                has_module_perms = user.has_module_perms(app_label)

                if has_module_perms:
                    perms = model_admin.get_model_perms(request)
        
                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.module_name)
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'perms': perms,
                        }
                        if perms.get('change', False):
                            try:
                                model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if perms.get('add', False):
                            try:
                                model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass

                        model_dict['order'] = model_admin.order if hasattr(model_admin, 'order') else 3
                        model_dict['separator'] = model_admin.separator if hasattr(model_admin, 'separator') else False

                        if app_label in app_dict:
                            app_dict[app_label]['models'].append(model_dict)
                        else:
                            app_dict[app_label] = {
                                'name': app_label.title(),
                                'icon': self._top_menu[app_label],
                                'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }
        app_list = app_dict.values()
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            print app['models']
            app['models'].sort(key=lambda x: x['order'])

        return app_list