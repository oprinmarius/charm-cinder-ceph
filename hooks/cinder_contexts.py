# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charmhelpers.core.hookenv import (
    service_name,
    is_relation_made,
    leader_get,
)

from charmhelpers.contrib.openstack.context import (
    OSContextGenerator,
)

from charmhelpers.contrib.openstack.utils import (
    get_os_codename_package,
    CompareOpenStackReleases,
)

CHARM_CEPH_CONF = '/var/lib/charm/{}/ceph.conf'


def ceph_config_file():
    return CHARM_CEPH_CONF.format(service_name())


class CephSubordinateContext(OSContextGenerator):
    interfaces = ['ceph-cinder']

    def __call__(self):
        """
        Used to generate template context to be added to cinder.conf in the
        presence of a ceph relation.
        """
        if not is_relation_made('ceph', 'key'):
            return {}
        service = service_name()
        os_codename = get_os_codename_package('cinder-common')
        if CompareOpenStackReleases(os_codename) >= "icehouse":
            volume_driver = 'cinder.volume.drivers.rbd.RBDDriver'
        else:
            volume_driver = 'cinder.volume.driver.RBDDriver'

        section = {service: [('volume_backend_name', service),
                             ('volume_driver', volume_driver),
                             ('rbd_pool', service),
                             ('rbd_user', service),
                             ('rbd_secret_uuid', leader_get('secret-uuid')),
                             ('rbd_ceph_conf', ceph_config_file())]}

        if CompareOpenStackReleases(os_codename) >= "mitaka":
            section[service].append(('report_discard_supported', True))

        if CompareOpenStackReleases(os_codename) >= "queens":
            section[service].append(('rbd_exclusive_cinder_pool', True))

        return {'cinder': {'/etc/cinder/cinder.conf': {'sections': section}}}
