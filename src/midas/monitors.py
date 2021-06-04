import logging

from spidermon import MonitorSuite, Monitor
from spidermon.contrib.actions.telegram.notifiers import SendTelegramMessageSpiderFinished
from spidermon.contrib.monitors.mixins import StatsMonitorMixin
from spidermon.contrib.scrapy.monitors import ErrorCountMonitor, UnwantedHTTPCodesMonitor
from spidermon.decorators import monitors


logging.getLogger('requests').setLevel('INFO')


@monitors.name('Item validation')
class ItemValidationMonitor(Monitor, StatsMonitorMixin):

    @monitors.name('No item validation errors')
    def test_no_item_validation_errors(self):
        validation_errors = getattr(
            self.stats, 'spidermon/validation/fields/errors', 0
        )
        self.assertEqual(
            validation_errors,
            0,
            msg='Found validation errors in {} fields'.format(
                validation_errors)
        )


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [
        UnwantedHTTPCodesMonitor,
        ItemValidationMonitor,
        ErrorCountMonitor,
    ]

    monitors_finished_actions = [
        SendTelegramMessageSpiderFinished,
    ]
