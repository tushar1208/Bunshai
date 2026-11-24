# main/signals.py
# Email notifications and Google Sheets backups are sent from the views
# (see views.notify), so only lightweight model hooks live here.
import logging

logger = logging.getLogger(__name__)
