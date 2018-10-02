# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class KDVisitLine(models.Model):
    _name = 'kd.visit.line'
    _rec_name = 'name'

    visit_id = fields.Many2one('kd.visit','Vist',required=True)
    name = fields.Char('양식명칭')
    desc = fields.Text('설명')