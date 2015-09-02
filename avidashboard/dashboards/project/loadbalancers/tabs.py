#    Copyright 2015, Avi Networks, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import messages
from django.conf import settings
import os
import shutil

from avidashboard import api

from avidashboard.dashboards.project.loadbalancers import tables


class CertificatesTab(tabs.TableTab):
    table_classes = (tables.CertificatesTable,)
    name = _("Certificates")
    slug = "certificates"
    template_name = "horizon/common/_detail_table.html"

    def get_certificatestable_data(self):
        try:
            tenant_name = self.request.user.tenant_name
            certificates = api.avi.certs_list(self.tab_group.request, tenant_name)
        except Exception as e:
            certificates = []
            messages.warning(self.tab_group.request, _("Unable to retrieve certificates"))
            #exceptions.handle(self.tab_group.request,
            #                  _('Unable to retrieve certificates list.'))
        return certificates


class AviUITab(tabs.Tab):
    name = "Analytics"
    slug = "analytics"
    preload = False
    template_set = False

    def set_template(self):
        if AviUITab.template_set:
            return
        template_dir = (os.path.dirname(os.path.abspath(__file__)) +
                        "/../../../templates")
        template_file = os.path.join(template_dir, "avi_analytics.html")
        if not os.path.exists(template_file):
            raise Exception("Missing Avi Tab Template")
        dest_file = os.path.join(settings.TEMPLATE_DIRS[0],
                                 "avi_analytics.html")
        shutil.copy(template_file, dest_file)
        AviUITab.template_set = True
        return

    def get_template_name(self, request):
        self.set_template()
        return "avi_analytics.html"

    def get_context_data(self, request, **kwargs):
        avi_session = api.avi.avisession(request)
        return {
            'controller_ip': avi_session.controller_ip,
            'csrf_token': avi_session.sess.headers["X-CSRFToken"],
            'session_id': avi_session.sess.cookies.get("sessionid"),
            'tenant_name': avi_session.tenant
        }
