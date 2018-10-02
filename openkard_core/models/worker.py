# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KdWorker(models.Model):
    _name = 'kd.worker'
    _inherits = {'res.partner': 'partner_id'}

    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128)
    birth_date = fields.Date('Birth Date')
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'),
         ('o', 'Other')], 'Gender')
    id_number = fields.Char('연구원 ID', size=64)
    already_partner = fields.Boolean('Already Partner')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")
    # category_id = fields.Many2one('op.category', 'Category')

    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    nationality = fields.Many2one('res.country', 'Nationality')

