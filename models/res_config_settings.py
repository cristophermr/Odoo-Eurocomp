from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    eurocomp_username = fields.Char(string='Eurocomp username', help="Eurocomp username")
    eurocomp_password = fields.Char(string='Eurocomp password', help="Eurocomp password")
    eurocomp_stock_min = fields.Integer(string='Stock Mimimun on system', help="Eurocomp stock min")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            eurocomp_username=get_param('eurocomp_username'),
            eurocomp_password=get_param('eurocomp_password'),
            eurocomp_stock_min=int(get_param('eurocomp_stock_min', default=0)),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('eurocomp_username', self.eurocomp_username)
        set_param('eurocomp_password', self.eurocomp_password)
        set_param('eurocomp_stock_min', self.eurocomp_stock_min)