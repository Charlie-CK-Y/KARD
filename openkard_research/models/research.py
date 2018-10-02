# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KdResearchType(models.Model):
    # 현재는 사용하지 않음.(18.05.27)
    _name = 'kd.research.type'
    _description = 'Research Type'

    name = fields.Char('Name', size=256, required=True)
    desc = fields.Text('Description')


class KdResearch(models.Model):
    _name = 'kd.research'
    _rec_name = 'research_title'
    _description = 'Research'
    _inherit = 'mail.thread'

    research_title = fields.Char('Research Name')
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')
    istemplate = fields.Boolean('template', default=False)
    worker_id = fields.Many2one('kd.worker', 'Administrator', required=True)

    description = fields.Text('Research information',default='Description of purpose and research')

    # One2many
    case_ids = fields.One2many('kd.case', 'research_id', 'Research Case(s)')

    # _sql_constraints = [
    #     ('unique_research_code',
    #      'unique(research_code)', 'Research code should be unique per research!'),
    # ]

    @api.multi
    def create_new_case(self):
        res = self.env['ir.model.data'].get_object_reference('openkard_research', 'act_open_kd_case_view')
        res_id = res and res[1] or False

        case_Obj = self.env['kd.case']



        domainDefaultVisitSet = [('state', '=', 'available'),('research_id','=',self.id),('isdefault','=',True)]
        siteDefaultVisitSet = self.env['kd.visitset'].sudo().search_read(domainDefaultVisitSet, ['id','name'])

        domainCurrentUser = [('id', '=', self.env.uid)]
        currentUser = self.env['res.users'].sudo().search_read(domainCurrentUser, ['name'])

        domainUserCase = [('create_uid', '=', self.create_uid.id), ('research_id', '=', self.id)]
        userCaseCount = self.env['kd.case'].sudo().search_count(domainUserCase)

        if siteDefaultVisitSet:
            newCase = case_Obj.create({'research_id': self.id, 'state': 'available','visitset_id':siteDefaultVisitSet[0]['id']})
        else:
            raise ValidationError(_('Error: There is no valid visit in the VisitSet.'))

        self.env.uid

        if siteDefaultVisitSet:
            newCase.name = self.research_title+'-'+currentUser[0]['name']+'#'+str(userCaseCount)


        if newCase.visitset_id:
            newCase.create_vistset(self.id)
        else:
            raise ValidationError(_('Error: There is no visitset template associated with research id.'))

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'kd.case',
            'target': 'current',
            'res_id': newCase.id,
            'context': {'default_research_id': self.id,
                        'default_istemplate': self.istemplate},
        }
