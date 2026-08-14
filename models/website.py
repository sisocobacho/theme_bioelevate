from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _force_terms_settings_on_company(self):
        terms_html = """<h1>Terms and Conditions</h1>
<p>Welcome to BioElevate!</p>
<p>These terms and conditions outline the rules and regulations for the use of BioElevate's Website, located at https://bioelevate.org.</p>
<p>By accessing this website, we assume you accept these terms and conditions. Do not continue to use BioElevate if you do not agree to take all of the terms and conditions stated on this page.</p>
<h4>Cookies</h4>
<p>The website uses cookies to help personalize your online experience. By accessing BioElevate, you agreed to use the required cookies.</p>
<p>A cookie is a text file that is placed on your hard disk by a web page server. Cookies cannot be used to run programs or deliver viruses to your computer. Cookies are uniquely assigned to you and can only be read by a web server in the domain that issued the cookie to you.</p>
<p>We may use cookies to collect, store, and track information for statistical or marketing purposes to operate our website. You have the ability to accept or decline optional Cookies. There are some required Cookies that are necessary for the operation of our website.</p>
<h4>License</h4>
<p>Unless otherwise stated, and/or its licensors own the intellectual property rights for all material on BioElevate. All intellectual property rights are reserved.</p>
<p>You must not:</p>
<ul>
    <li>Copy or republish material from BioElevate</li>
    <li>Sell, rent, or sub-license material from BioElevate</li>
    <li>Reproduce, duplicate or copy material from BioElevate</li>
    <li>Redistribute content from BioElevate</li>
</ul>
<h4>Content Liability</h4>
<p>We shall not be held responsible for any content that appears on your Website. You agree to protect and defend us against all claims that are raised on your Website.</p>
<h4>Reservation of Rights</h4>
<p>We reserve the right to request that you remove all links or any particular link to our Website. We also reserve the right to amend these terms and conditions at any time.</p>
<h4>Disclaimer</h4>
<p>To the maximum extent permitted by applicable law, we exclude all representations, warranties, and conditions relating to our website and the use of this website.</p>
<p>As long as the website and the information and services on the website are provided free of charge, we will not be liable for any loss or damage of any nature.</p>
"""
        self.env["ir.config_parameter"].sudo().set_param("account.use_invoice_terms", "True")
        for website in self:
            website.company_id.sudo().write(
                {
                    "terms_type": "html",
                    "invoice_terms_html": terms_html,
                }
            )
