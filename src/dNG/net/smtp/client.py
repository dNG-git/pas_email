# -*- coding: utf-8 -*-

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

# pylint: disable=import-error, no-name-in-module

from copy import copy
from smtplib import LMTP, SMTP, SMTP_SSL, SMTPServerDisconnected

from dNG.data.rfc.email.message import Message
from dNG.data.settings import Settings
from dNG.runtime.io_exception import IOException
from dNG.runtime.named_loader import NamedLoader
from dNG.runtime.type_exception import TypeException
from dNG.runtime.value_exception import ValueException

class Client(object):
    """
The SMTP client is used to send e-mails with the configured server.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: email
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Client)

:since: v1.0.0
        """

        self._log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self._message = None
        """
e-mail message instance
        """
        self.timeout = 0
        """
Request timeout value
        """

        Settings.read_file("{0}/settings/pas_email.json".format(Settings.get("path_data")), True)
        Settings.read_file("{0}/settings/pas_smtp_client.json".format(Settings.get("path_data")), True)

        self.timeout = int(Settings.get("pas_smtp_client_timeout", 30))
    #

    @property
    def message(self):
        """
Returns the e-mail message instance set.

:return: (object) e-mail message instance
:since:  v1.0.0
        """

        return self._message
    #

    @message.setter
    def message(self, message):
        """
Sets the e-mail message instance of this instance.

:param message: e-mail message instance

:since: v1.0.0
        """

        self.set_message(message, True)
    #

    def _get_lmtp_connection(self):
        """
Returns an established LMTP connection.

:return: (object) LMTP connection
:since:  v1.0.0
        """

        smtp_options = { }
        if (Settings.is_defined("pas_smtp_client_sender_hostname")): smtp_options['local_hostname'] = Settings.get("pas_smtp_client_sender_hostname")

        _return = (LMTP(Settings.get("pas_smtp_client_lmtp_host"), int(Settings.get("pas_smtp_client_lmtp_port", 24)))
                   if (Settings.is_defined("pas_smtp_client_lmtp_host")) else
                   LMTP(Settings.get("pas_smtp_client_lmtp_path_name"))
                  )

        return _return
    #

    def _get_smtp_connection(self):
        """
Returns an established SMTP connection.

:return: (object) SMTP connection
:since:  v1.0.0
        """

        smtp_host = Settings.get("pas_smtp_client_host", "localhost")
        smtp_port = int(Settings.get("pas_smtp_client_port", 25))
        smtp_options = { }

        is_tls_connection = Settings.get("pas_smtp_client_tls", False)
        ssl_cert_file_path_name = ""
        ssl_key_file_path_name = ""

        if (Settings.is_defined("pas_smtp_client_ssl_cert_file") and Settings.is_defined("pas_smtp_client_ssl_key_file")):
            ssl_cert_file_path_name = Settings.get("pas_smtp_client_ssl_cert_file")
            ssl_key_file_path_name = Settings.get("pas_smtp_client_ssl_key_file")

            if (ssl_cert_file_path_name + ssl_key_file_path_name == ""): raise IOException("TLS requested for incomplete configuration")
        #

        if (ssl_cert_file_path_name + ssl_key_file_path_name != "" and (not is_tls_connection)):
            smtp_options['certfile'] = ssl_cert_file_path_name
            smtp_options['keyfile'] = ssl_key_file_path_name
        #

        if (Settings.is_defined("pas_smtp_client_sender_hostname")): smtp_options['local_hostname'] = Settings.get("pas_smtp_client_sender_hostname")

        _return = (SMTP_SSL(smtp_host, smtp_port, timeout = self.timeout, **smtp_options)
                   if ("keyfile" in smtp_options) else
                   SMTP(smtp_host, smtp_port, timeout = self.timeout, **smtp_options)
                  )

        if (is_tls_connection): _return.starttls(ssl_key_file_path_name, ssl_cert_file_path_name)

        return _return
    #

    def send(self):
        """
Sends a message.

:since: v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.send()- (#echo(__LINE__)#)", self, context = "pas_email")

        if (self.message is None): raise IOException("No message defined to be send")
        if (not self.message.is_recipient_set): raise ValueException("No recipients defined for e-mail")
        if (not self.message.is_subject_set): raise IOException("No subject defined for e-mail")

        bcc_list = self.message.bcc
        cc_list = self.message.cc
        to_list = self.message.to

        rcpt_list = to_list
        if (len(bcc_list) > 0): rcpt_list = Client._filter_unique_list(rcpt_list, bcc_list)
        if (len(cc_list) > 0): rcpt_list = Client._filter_unique_list(rcpt_list, cc_list)

        is_auth_possible = False
        smtp_user = None
        smtp_password = None

        if (Settings.is_defined("pas_smtp_client_user") and Settings.is_defined("pas_smtp_client_password")):
            is_auth_possible = True
            smtp_user = Settings.get("pas_smtp_client_user")
            smtp_password = Settings.get("pas_smtp_client_password")
        #

        smtp_connection = None

        try:
            smtp_connection = (self._get_lmtp_connection()
                               if (Settings.is_defined("pas_smtp_client_lmtp_host")
                                   or Settings.is_defined("pas_smtp_client_lmtp_path_name")
                                  )
                               else self._get_smtp_connection()
                              )

            if (is_auth_possible): smtp_connection.login(smtp_user, smtp_password)

            if (not self.message.is_sender_set):
                self.message.sender = (Settings.get("pas_email_sender_public")
                                       if (Settings.is_defined("pas_email_sender_public")) else
                                       Settings.get("pas_email_address_public")
                                      )
            #

            sender = self.message.sender

            smtp_connection.sendmail(sender, rcpt_list, self.message.as_string())

            self.message = None
        finally:
            try:
                if (smtp_connection is not None): smtp_connection.quit()
            except SMTPServerDisconnected: pass
        #
    #

    def set_message(self, message, overwrite = False):
        """
Sets the message body of the e-mail.

:param message: Message instance
:param overwrite: True to overwrite the current (non-empty) cache

:since: v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_message()- (#echo(__LINE__)#)", self, context = "pas_email")

        if (not isinstance(message, Message)): raise TypeException("Body not given in a supported type")
        if ((not overwrite) and self.message is not None): raise ValueException("Body is already set")

        # Copy message as we manipulate it in "send()"
        self.message = copy(message)
    #

    @staticmethod
    def _filter_unique_list(source_list, additional_list):
        """
Returns a list where each entry is unique.

:return: (list) Unique list of entries given
:since:  v1.0.0
        """

        _return = source_list

        for value in additional_list:
            if (value not in _return): _return.append(value)
        #

        return _return
    #
#
