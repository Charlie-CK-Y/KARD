# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class KDVistSet(models.Model):
    '''
    Visit Template
    '''
    _name = 'kd.visitset'
    _description = 'Visit Set'

    name = fields.Char('Name',default='visit set name')
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')
    # Default 인 경우에만 Case에서 VisitSet를 사용할 수 있다.
    isdefault = fields.Boolean('Default Visit Set',default=False)
    desc = fields.Text('Description')

    # Visit에 연결된 Visit Template 목록
    # VisitSet 일괄 생성 시 사용 함
    research_id = fields.Many2one('kd.research','Use research',required=True)
    visitset_line_ids = fields.One2many('kd.visitset.line','visitset_id','Visit Set(s)')

class KDUserVistSet(models.Model):
    '''
    User Visit Template
    '''

    _name = 'kd.visitset.user'
    _description = 'User Visit Set'

    name = fields.Char('Name',default='User Visit set name')
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')

    visitset_id = fields.Many2one('kd.visitset', 'VisitSet ID', required=True)
    user_id = fields.Many2one('res.users', string='Create User')
