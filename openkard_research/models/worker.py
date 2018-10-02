# -*- coding: utf-8 -*-

from odoo import models, fields


class KdWorker(models.Model):
    '''
    Openkard core의 Worker을 사용하기 위함.
    '''
    _inherit = 'kd.worker'

    research_id = fields.Many2one('kd.research', 'Research')
