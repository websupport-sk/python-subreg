# -*- coding: utf-8 -*-

# Copyright (c) 2013 Petr Jerabek
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

import re
from SOAPpy import SOAPProxy, typedArrayType, Types

from .exceptions import ApiError


class Api(object):
    """Python wrapper around the subreg.cz SOAP API"""

    endpoint = 'https://soap.subreg.cz/cmd.php'

    response = None
    """Last parsed response from API"""

    raw_response = None
    """Last raw response from API"""

    def __init__(self, username=None, password=None):
        """"""
        self.token = None
        self.client = SOAPProxy(self.endpoint)
        if username and password:
            self.login(username, password)

    def login(self, username=None, password=None):
        """
        User login to API

        :param str username: Username for login
        :param str password: Password

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Login
        """
        kwargs = {'login': username, 'password': password}
        response = self._request('Login', kwargs)
        self.token = response['ssid']

    def check_domain(self, domain):
        """
        Check if domain is available or not

        :param str domain: Domain for check availability

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Check_Domain
        """
        kwargs = {'domain': domain}
        response = self._request('Check_Domain', kwargs)
        if response['avail'] == 1:
            return True
        return False

    def info_domain(self, domain):
        """
        Get informations about a single domain from your account

        :param str domain: Domain name for requested informations

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Info_Domain
        """
        kwargs = {'domain': domain}
        response = self._request('Info_Domain', kwargs)
        return response

    def info_domain_cz(self, domain):
        """
        Get informations about a single .CZ domain

        :param str domain: Domain name for requested informations

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Info_Domain_CZ
        """
        kwargs = {'domain': domain}
        response = self._request('Info_Domain_CZ', kwargs)
        return response

    def domains_list(self):
        """
        Get all domains from your account

        :return dict
            :key `domains`: dict of domains
                :key `name`: Domain name
                :key `expire`: Domain expiration date
            :key `count`: Domains count

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Domains_List
        """
        return self._request('Domains_List')

    def set_autorenew(self, domain, autorenew):
        """
        Set autorenew policy for your domain.
        By default, domain is deleted when it expire.
        You can set autorenew flag to AUTORENEW, then it will use your credit
        to renew automatically. RENEWONCE will cause renew only for next year.

        :param str domain: Registered domain
        :param str autorenew: Autorenew setting, allowed values:
            EXPIRE, AUTORENEW, RENEWONCE

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Set_Autorenew
        """
        if autorenew in ['EXPIRE', 'AUTORENEW', 'RENEWONCE']:
            kwargs = {'domain': domain, 'autorenew': autorenew}
            try:
                self._request('Set_Autorenew', kwargs)
                return True
            except ApiError:
                return False
        return False

    def create_contact(self, contact):
        """
        Create contact in Subreg DB

        :param dict contact:    Data about contact
            string	name:        First name of contact
            string	surname:     Second name of contact
            string	org:         Organization name (optionally)
            string	street:      Address of contact
            string	city:        City of contact
            string	pc:          ZIP code of contact
            string	sp:          State of contact (optionally)
            string	cc:          ISO Country Code of contact
            string	phone:       Phone of contact in format +1.234567890
            string	fax:         Faxsimile of contact in format +1.234567890 (optionally)
            string	email:       Email of contact
            dict	params:      Details for fred contacts (.CZ, .EE) (optionally)
                string	regid:         NIC ID
                string	notify_email:  Email for NIC notify
                string	vat:           VAT Number
                string	ident_type:    (op,passport,mpsv,ico,birthday)
                string	ident_number:
                dict	disclose:      (voice,fax,email,vat,ident,notify_email)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Create_Contact
        """
        kwargs = {'contact': contact}
        response = self._request('Create_Contact', kwargs)
        return response

    def update_contact(self, contact):
        """
        Update contact

        :param dict  contact:  Data about contact
            string  id:      ID of updating contact
            string  name:    Name of person (optionally)
            string  surname: Surname of person (optionally)
            string  street:  Address of contact (optionally)
            string  city:    City of contact (optionally)
            string  pc:      ZIP code of contact (optionally)
            string  sp:      State of contact (optionally)
            string  cc:      ISO Country Code of contact (optionally)
            string  phone:   Phone of contact in format +1.234567890 (optionally)
            string  fax:     Faxsimile of contact in format +1.234567890 (optionally)
            string  email:	Email of contact (optionally)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Update_Contact
        """
        kwargs = {'contact': contact}
        response = self._request('Update_Contact', kwargs)
        return response

    def info_contact(self, contact_id):
        """
        Get informations about a single contact from your account

        :param int contact_id: ID of your querying contact

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Info_Contact
        """
        kwargs = {'contact': [contact_id]}
        response = self._request('Info_Contact', kwargs)
        return response

    def contacts_list(self):
        """
        Get all contacts from your account

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Contacts_List
        """
        return self._request('Contacts_List')

    def check_object(self, _id, _object):
        """
        Check if object is available or not (only CZ,EE)

        :param int _id: ID for check availability
        :param str _object: contact, nsset, keyset (only CZ, EE)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Check_Object
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def info_object(self, _id, _object):
        """
        Info about NIC object (only CZ,EE)

        :param int _id: ID for info
        :param str _object: contact, nsset, keyset (only CZ, EE)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Info_Object
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def make_order(self, order):
        """
        Create a new order (CreateDomain, ModifyDomain, RenewDomain, ... )


        :param array	order   See what that means on URL below

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Make_Order
        """
        response = self._request("Make_Order", order)
        return response

    def info_order(self, order_id):
        """
        Info about existing order

        :param int order_id: Order ID

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Info_Order
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def get_credit(self):
        """
        Get status of your credit

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Get_Credit
        """
        return self._request('Get_Credit')

    def get_accountings(self, from_date, to_date):
        """
        Get financial statements from account

        :param from_date: Date (YYYY-mm-dd)
        :param to_date: Date (YYYY-mm-dd)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Get_Accountings
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def client_payment(self, username, amount, currency):
        """
        Add credit to your sub-user. This command WILL generate invoice,
        if you want just correct current amount of credit for any reason,
        please use command Credit_Correction.

        :param str username: Login username of the use you want to add credit
        :param str amount: Amount of money to add
        :param str currency: Currency of added credit

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Client_Payment
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def credit_correction(self, username, amount, reason):
        """
        Correct credit amount of your sub-users. The amount you specify in this
        command will be added to current amount. Use negative values for
        subtracting credit. Please note that currency will depend on
        current user setting.

        :param str username: Login username of the user you want to add credit
        :param float amount: Amount of money to add/subtract
        :param str reason: Human readable reason for this operation

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Credit_Correction
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def pricelist(self):
        """
        Get pricelist from account

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Pricelist
        """
        return self._request('Pricelist')

    def prices(self, tld):
        """
        Get Prices for TLD from account

        :type str tld: Requested TLD

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Prices
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def get_pricelist(self, pricelist):
        """
        Return all price information in specified pricelist.

        :param str pricelist: Identificator of the pricelist you want to download.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Get_Pricelist
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def set_prices(self, pricelist, tld, currency, prices=None):
        """
        Change prices in specified pricelist.

        :param str pricelist: Identificator of the pricelist you want to download.
        :param str tld: TLD for which you want to change prices.
        :param str currency: Currency code the prices use.
        :param str prices: List of operations with price

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Set_Prices
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def download_document(self, document_id):
        """
        Get document information and base64 encoded document that you have
        uploaded or generated on your account.

        :param int document_id: Document ID, you can get it in response of
                            `Upload_Document` or by `List_Documents`.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Download_Document
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def upload_document(self, name, document, _type=None, filetype=None):
        """
        Upload document to your account, for use as identification document,
        registration request etc.

        :param str name: Filename of the document, including extension
        :param str document: base64 encoded document
        :param str _type: Type of the document
                     (https://soap.subreg.cz/manual/?cmd=Document_Types)
        :param str filetype: MIME type of the file

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Upload_Document
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def list_documents(self):
        """
        List documents uploaded or generated on your account.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=List_Documents
        """
        return self._request('List_Documents')

    def users_list(self):
        """
        Retrieve list of all your sub-users

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Users_List
        """
        return self._request('Users_List')

    def get_dns_zone(self, domain):
        """
        List of DNS records for specified domain.

        :param str domain: Registered domain

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Get_DNS_Zone
        """
        kwargs = {'domain': domain}
        response = self._request('Get_DNS_Zone', kwargs)
        try:
            return response['records']
        except KeyError:
            return []

    def add_dns_zone(self, domain, template=None):
        """
        Add domain to DNS using previously created template.

        :param str domain: Registered domain
        :param str template: DNS template ID or template name

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Add_DNS_Zone
        """
        kwargs = {'domain': domain}
        if not template:
            kwargs['template'] = template
        try:
            self._request('Add_DNS_Zone', kwargs)
            return True
        except ApiError:
            return False

    def delete_dns_zone(self, domain):
        """
        Remove ALL DNS records for specified domain.

        :param str domain: Registered domain

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Delete_DNS_Zone
        """
        kwargs = {'domain': domain}
        response = self._request('Delete_DNS_Zone', kwargs)
        return response

    def set_dns_zone(self, domain, records):
        """
        Specify complete set of records for certain zone.
        Specified records will replace ALL present records.

        :param str domain: Registered domain
        :param list records: List of dicts of records

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Set_DNS_Zone
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def add_dns_record(self, domain, record):
        """
        Add DNS record to zone.

        :param str domain: Registered domain
        :param dict record: dict with params

            :key name: Hostname (part of hostname, without registered domain)
            :key type: Type of DNS record
            :key content: Value of this record (IP address, hostname, text
                value,..)
            :key prio: Priority of this record (MX records only)
            :key ttl: TTL value

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Add_DNS_Record
        """
        if not isinstance(record, dict):
            raise TypeError
            # remove leading .
        record['content'] = re.sub('\.$', '', record['content'])
        kwargs = {'domain': domain, 'record': record}
        try:
            response = self._request('Add_DNS_Record', kwargs)
            return response['record_id']
        except (KeyError, ApiError):
            return False

    def modify_dns_record(self, domain, record):
        """
        Midify DNS record at zone.

        :param str domain: Registered domain
        :param dict record: dict with ID of existing record

            :key id: ID of existing record
            :key name: Hostname (part of hostname, without registered domain)
            :key type: Type of DNS record
            :key content: Value of this record (IP address, hostname, text
                value,..)
            :key prio: Priority of this record (MX records only)
            :key ttl: TTL value

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Modify_DNS_Record
        """
        if not isinstance(record, dict):
            raise TypeError
        error_message = 'You must specify `record.id` when edit record.'
        try:
            if not record['id']:
                raise Exception(error_message)
        except KeyError:
            raise Exception(error_message)
        kwargs = {'domain': domain, 'record': record}
        try:
            self._request('Modify_DNS_Record', kwargs)
            return True
        except (KeyError, ApiError):
            return False

    def delete_dns_record(self, domain, record_id):
        """
        Remove DNS record from zone.

        :param str domain: Registered domain
        :param int record_id: ID of existing record

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Delete_DNS_Record
        """
        if not record_id:
            raise TypeError
        kwargs = {'domain': domain, 'record': {'id': record_id}}
        try:
            self._request('Delete_DNS_Record', kwargs)
            return True
        except ApiError:
            return False

    def poll_get(self):
        """
        Get current poll message

        .. seealso:: https://soap.subreg.cz/manual/?cmd=POLL_Get
        """
        return self._request('POLL_Get')

    def poll_ack(self, poll_id):
        """
        Ack current poll message

        :param int poll_id: POLL ID

        .. seealso:: https://soap.subreg.cz/manual/?cmd=POLL_Ack
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def oib_search(self, oib):
        """
        List domains registered for certain OIB, and get the number of domains
        possible to register for this OIB.

        :param str oib: Croatian OIB number

        .. seealso:: https://soap.subreg.cz/manual/?cmd=OIB_Search
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    # -- Orders ----------------------------------------------------------------

    def create_domain(self, domain, registrant, admin, tech, nss, authid="", period=1):
        """
            Create new domain

            For DNSSEC extension please see full

            :param string  domain       domain name
            :param string  registrant   contact ID for registrant
            :param string  admin        contact ID for admin
            :param string  tech         contact ID for tech
            :param dict    nss          NS servers
            :param string  authid       password to transfer/editation(?)
            :param int     period       number of years

            Return dict with status and orderid.

            .. seealso:: https://soap.subreg.cz/manual/?cmd=Create_Domain
        """
        order = {
            "domain": domain,
            "type": "Create_Domain",
            "params": {
                "registrant": {"id": registrant},
                "contacts": {
                    "admin": {"id": admin},
                    "tech": {"id": tech},
                },
                "ns": {"hosts": nss},
                "params": {"authid": authid},
                "period": period,
            }
        }
        return self.make_order(order)

    def transfer_domain(self, domain, authid=""):
        """
            Transfer domain

            :param string  domain       domain name
            :param string  authid       password for transfer

            Return dict with status and orderid.

            .. seealso:: https://soap.subreg.cz/manual/?cmd=Transfer_Domain
        """
        order = {
            "domain": domain,
            "type": "Transfer_Domain",
            "params": {
                "params": {"authid": authid},
            }
        }
        return self.make_order(order)

    def account_transfer_domain(self):
        """
        Transfer domain between two Subreg.CZ accounts.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=AccountTransfer_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def transfer_approve_domain(self):
        """
        Transfer Approve domain between two registrars

        .. seealso:: https://soap.subreg.cz/manual/?cmd=TransferApprove_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def transfer_deny_domain(self):
        """
        Transfer Deny domain between two registrars

        .. seealso:: https://soap.subreg.cz/manual/?cmd=TransferDeny_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def transfer_cancel_domain(self):
        """
        Transfer Cancel domain between two registrars

        .. seealso:: https://soap.subreg.cz/manual/?cmd=TransferCancel_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def sk_change_owner_domain(self):
        """
        Initiate owner change for .SK domain. During processing of this order,
        filled form will be generated onto your account.
        You can then download it using our web interface or using
        `Download_Document <https://soap.subreg.cz/manual/?cmd=Download_Document>`_.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=SKChangeOwner_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def modify_domain(self, domain, admin, tech, nss, authid):
        """
        Modify existing domain to new values.
        For DNSSEC extension please see full
        specification `here <https://soap.subreg.cz/manual/?cmd=DNSSEC>`_.

        :param string  domain       domain name
        :param string  admin        contact ID for admin
        :param string  tech         contact ID for tech
        :param dict    nss          NS servers
        :param string  authid       password to transfer/editation(?)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Modify_Domain
        .. exception:: NotImplementedError
        """
        
        order = {
            "type": "Modify_Domain",
            "domain": domain,
            "params": {
                "contacts": {
                    "admin": {
                        "regid": admin,
                    },
                    "tech": {
                        "regid": tech,
                    },
                },
                "ns": {
                    "hosts": nss,
                },
                "params": {
                    "authid": authid,
                    "status": {"clientTransferProhibited"},
                }
            }
        }
        return self.make_order(order)

    def modify_domain_dnssec(self, domain, records=None, dsdata=None):
        """
        Modify dnssec for existing domain

        :param string  domain       domain name
        :param string  records      dnssec key data
        :param string  dsdata       dnssec ds data
        """

        data = {
            "order": {
                "type": "ModifyNS_Domain",
                "domain": domain,
                "params": {
                    "params": {
                        "records": records,
                        "dsdata": dsdata,
                    }
                }
            }
        }
        return self.make_order(data)

    def modify_ns_domain(self, domain, nss):
        """
        Modify existing domain to new values.
        For DNSSEC extension please see full
        specification `here <https://soap.subreg.cz/manual/?cmd=DNSSEC>`_.

        :param string  domain       domain name
        :param dict    nss          NS servers

        .. seealso:: https://soap.subreg.cz/manual/?cmd=ModifyNS_Domain
        """

        order = {
            "type": "ModifyNS_Domain",
            "domain": domain,
            "params": {
                "ns": {
                    "hosts": nss,
                }
            }
        }
        return self.make_order(order)

    def delete_domain(self, domain, reason):
        """
        Delete a existing domain from your account

        :param string  domain       domain name
        :param string  reason       reason to deleate

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Delete_Domain
        """

        order = {
            "type": "Delete_Domain",
            "domain": domain,
            "params": {
                "reason": reason,
            }
        }
        return self.make_order(order)

    def restore_domain(self, domain):
        """
        Restore a deleted domain from your account

        :param string  domain       domain name

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Restore_Domain
        .. exception:: NotImplementedError
        """

        order = {
            "type": "Restore_Domain",
            "domain": domain,
        }
        return self.make_order(order)

    def renew_domain(self, domain, period):
        """
        Renew a existing domain from your account

        :param string  domain       domain name
        :param int     period       amount of years

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Renew_Domain
        """

        order = {
            "type": "Restore_Domain",
            "domain": domain,
            "params": {
                "period": period,
            }
        }
        return self.make_order(order)

    def backorder_domain(self):
        """
        Create a backorder order. We will register domain after deletion
        from registry

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Backorder_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def preregister_domain(self):
        """
        This order type is for new TLDs or liberation rules of existing TLDs
        domain pre-registration

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Preregister_Domain
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def create_object(self):
        """
        Creates new nsset or keyset.
        Only for registries with such capability (for example CZ-NIC or Eurid)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Create_Object
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def transfer_object(self):
        """
        Transfer object between two registrars (CZ-NIC)

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Transfer_Object
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def update_object(self):
        """
        .. seealso:: https://soap.subreg.cz/manual/?cmd=Update_Object
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def transfer_ru_request(self):
        """
        Transfer (change partner) of all domains on specified NIC-D account to
        Subreg.CZ.
        If you want to transfer just one .ru domain, you need to create new
        NIC-D account for that domain.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=TransferRU_Request
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def create_host(self):
        """
        Create new delegated host object.
        It is possible to specify multiple IPv4 and IPv6 addresses of the host.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Create_Host
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def update_host(self):
        """
        Change IP addresses of delegated host object.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Update_Host
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def delete_host(self):
        """
        Delete delegated host object.
        It is only possible to delete host when it is no longer used.

        .. seealso:: https://soap.subreg.cz/manual/?cmd=Delete_Host
        .. exception:: NotImplementedError
        """
        raise NotImplementedError

    def set_google_mx_records(self, domain):
        """
        Set Google MX rerods.
        Specified records will replace ALL present MX records.
        """
        records = self.get_dns_zone(domain)
        for record in records:
            # delete all mx records
            if record['type'] == 'MX':
                self.delete_dns_record(domain, record['id'])

        records = [
            dict(content='ASPMX.L.GOOGLE.COM.', prio=1),
            dict(content='ALT1.ASPMX.L.GOOGLE.COM.', prio=5),
            dict(content='ALT2.ASPMX.L.GOOGLE.COM.', prio=5),
            dict(content='ASPMX2.GOOGLEMAIL.COM.', prio=10),
            dict(content='ASPMX3.GOOGLEMAIL.COM.', prio=10),
        ]
        for record in records:
            record['ttl'] = 3600
            record['type'] = 'MX'
            self.add_dns_record(domain, record)

    def _request(self, command, kwargs=None):
        """Make request parse response"""
        if kwargs is None:
            kwargs = dict()
        if self.token:
            kwargs['ssid'] = self.token
        method = getattr(self.client, command)
        raw_response = method(**dict(data=kwargs))
        response = self._parse_response(raw_response)
        self.response = response
        self.raw_response = raw_response
        if response:
            if response['status'] == 'error':
                raise ApiError(
                    message=response['error']['errormsg'],
                    major=response['error']['errorcode']['major'],
                    minor=response['error']['errorcode']['minor']
                )
            return response.get('data')
        raise Exception('Fatal error.')

    def _parse_response(self, response):
        """Recursively parse response"""
        result = dict()
        if hasattr(response, 'item'):
            result = self._parse_response(response.item)
        elif hasattr(response, 'key'):
            if isinstance(response.value, str) or \
                    isinstance(response.value, int):
                result = {response.key: response.value}
            else:
                result = {response.key: self._parse_response(response.value)}
        elif isinstance(response, typedArrayType):
            result = list()
            for item in response:
                returned = self._parse_response(item)
                result.append(returned)
        elif isinstance(response, Types.arrayType):
            result = list()
            for item in response:
                returned = self._parse_response(item)
                result.append(returned)
        elif isinstance(response, list):
            for item in response:
                returned = self._parse_response(item)
                if isinstance(returned, dict):
                    result = dict(result.items() + returned.items())
        elif isinstance(response, str):
            result=response
        elif isinstance(response, float):
            result=response
        return result
