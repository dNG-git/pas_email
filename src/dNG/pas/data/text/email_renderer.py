# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;email

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasEMailVersion)#
#echo(__FILEPATH__)#
"""

from dNG.pas.data.settings import Settings
from dNG.pas.data.text.l10n import L10n

class EMailRenderer(object):
#
	"""
The "EMailRenderer" is responsible of creating a formatted text body.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: email
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	REASON_FOR_VALIDATION = 1
	"""
Send for validation or double opt-in
	"""
	REASON_FROM_ADMINISTRATION = 2
	"""
Send from an administrator
	"""
	REASON_FROM_SEPARATE_USER = 3
	"""
Send by a separate user
	"""
	REASON_FROM_SYSTEM = 4
	"""
Send by a separate user
	"""
	REASON_ON_DEMAND = 5
	"""
On demand of the user or an action the user initialized
	"""

	def __init__(self, l10n = None):
	#
		"""
Constructor __init__(EMailRenderer)

:param l10n: L10n instance

:since: v0.1.00
		"""

		self.l10n = l10n
		"""
L10n instance
		"""

		Settings.read_file("{0}/settings/pas_email.json".format(Settings.get("path_data")))

		if (self.l10n is None): self.l10n = L10n.get_instance()
		lang = self.l10n.get_lang()

		L10n.init("core", lang)
		L10n.init("pas_core", lang)
		L10n.init("pas_email", lang)
	#

	def _render_reason(self, reason):
	#
		"""
Render header, body and footer suitable for e-mail delivery.

:param body: Preformatted e-mail body
:param reason: Reason for automated delivery

:return: (str) Rendered e-mail body
:since:  v0.1.00
		"""

		_return = None

		if (reason == EMailRenderer.REASON_FOR_VALIDATION): _return = self.l10n.get("pas_email_reason_for_validation")
		elif (reason == EMailRenderer.REASON_FROM_ADMINISTRATION): _return = self.l10n.get("pas_email_reason_from_administration")
		elif (reason == EMailRenderer.REASON_FROM_SEPARATE_USER): _return = self.l10n.get("pas_email_reason_from_separate_user")
		elif (reason == EMailRenderer.REASON_ON_DEMAND): _return = self.l10n.get("pas_email_reason_on_demand")

		if (_return is None): _return = self.l10n.get("pas_email_reason_from_system")
		return _return.strip()
	#

	def render(self, body, reason = 0):
	#
		"""
Render header, body and footer suitable for e-mail delivery.

:param body: Preformatted e-mail body
:param reason: Reason for automated delivery

:return: (str) Rendered e-mail body
:since:  v0.1.00
		"""

		email_reason = self._render_reason(reason)
		lang = self.l10n.get_lang()

		header = Settings.get_lang_associated("pas_email_header", lang)
		header = (email_reason if (header is None) else "{0}\n\n{1}".format(header, email_reason))

		footer = Settings.get_lang_associated("pas_email_footer", lang, "(c) All rights reserved")

		_return = """
{0}
---

{1}

---
{2}
		""".format(header,
		           body.strip(),
		           footer
		          )

		return _return.strip()
	#
#

##j## EOF