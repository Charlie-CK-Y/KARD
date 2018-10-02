# -*- coding: utf-8 -*-
from odoo import models, fields


class KdVisitsetLine(models.Model):
    _name = 'kd.visitset.line'
    _rec_name = 'name'

    name = fields.Char('name',default='unknown')
    visit_id = fields.Many2one('kd.visit', 'Visit', required=True)
    visitset_id = fields.Many2one('kd.visitset', string='Visit Set(s)', ondelete='cascade')