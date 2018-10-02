# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime

from odoo import models, fields, api, _


class KdItemsetLine(models.Model):
    _name = 'kd.itemset.line'
    _rec_name = 'name'

    name = fields.Char('name',default='unknown')
    item_id = fields.Many2one('kd.item', 'Item', required=True)
    itemset_id = fields.Many2one('kd.itemset', string='Item Set(s)')


    #
    #
    # @api.model
    # def create(self, vals):
    #     res = super(KdItemsetLine, self).create(vals)
    #     res.name = 'ItemSet No #' + str(res.id)
    #
    #     return res