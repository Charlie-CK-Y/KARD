# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KdItemSet(models.Model):
    _name = 'kd.itemset'
    _description = 'Item Set'

    name = fields.Char('Name', size=256, default='unknown')
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')
    desc = fields.Text('Description')

    itemset_line_ids = fields.One2many('kd.itemset.line', 'itemset_id', 'Item Set(s)')
