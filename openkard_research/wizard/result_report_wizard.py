# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResultAnalysis(models.TransientModel):
    _name = 'kd.result.analysis'

    research_id = fields.Many2one('kd.research','Research',required=True)
    case_id = fields.Many2one('kd.case','Case',required=True)
    visit_id = fields.Many2one('kd.visit','Visit',required=True)

    # start_date = fields.Date('Start Date', default=time.strftime('%Y-%m-01'), required=True)
    # end_date = fields.Date('End Date', required=True)

    @api.multi
    def print_report(self):
        # start_date = fields.Date.from_string(self.start_date)
        # end_date = fields.Date.from_string(self.end_date)
        # if start_date > end_date:
        #     raise ValidationError(_("End Date cannot be set before \
        #         Start Date."))
        # else:
        data = self.read(['research_id','case_id','visit_id'])[0]
        return self.env['report'].get_action(
            self, 'openkard_research.report_result_analysis',
            data=data)