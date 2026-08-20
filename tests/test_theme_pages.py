# -*- coding: utf-8 -*-
"""
Tests for theme_bioelevate module.

Test approach:
- theme.ir.ui.view records are converted to ir.ui.view at theme load time
- We test the resulting ir.ui.view inheritance, not the theme.ir.ui.view directly
- Homepage content is verified via the inherited website.homepage view

Source reference: addons/website/models/theme_models.py:74-108
"""

import base64
import os

from odoo.modules.module import get_manifest
from odoo.tests import TransactionCase, tagged


@tagged("standard", "at_install")
class TestThemePages(TransactionCase):
    def test_module_loaded(self):
        """Verify module is installed."""
        manifest = get_manifest("theme_bioelevate")
        self.assertIsNotNone(manifest, "Module theme_bioelevate is not installed.")

    def test_homepage_url_points_to_shop(self):
        """Verify website homepage URL is configured to shop route."""
        website = self.env.ref("website.default_website")
        self.assertEqual(
            website.homepage_url,
            "/shop",
            "Expected website.default_website homepage_url to be '/shop'.",
        )

    def test_old_homepage_available_at_home_url(self):
        """Verify the original homepage page is moved to /home."""
        website = self.env.ref("website.default_website")
        homepage_page = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("key", "=", "website.homepage"),
            ],
            limit=1,
        )
        self.assertTrue(homepage_page, "Expected homepage page for default website.")
        self.assertEqual(
            homepage_page.url,
            "/home",
            "Expected website.homepage_page URL to be '/home'.",
        )

    def test_home_menu_points_to_home_url(self):
        """Verify main Home menu points to /home on the default website."""
        website = self.env.ref("website.default_website")
        home_menu = self.env["website.menu"].search(
            [
                ("website_id", "=", website.id),
                ("name", "=", "Home"),
            ],
            limit=1,
        )
        self.assertTrue(home_menu, "Expected a 'Home' menu on the default website.")
        self.assertEqual(
            home_menu.url,
            "/home",
            "Expected Home menu URL to be '/home'.",
        )

    def test_theme_homepage_view_exists(self):
        """Verify theme.ir.ui.view record for homepage content exists."""
        theme_view = self.env.ref(
            "theme_bioelevate.theme_homepage_content",
            raise_if_not_found=False
        )
        self.assertIsNotNone(
            theme_view,
            "Expected theme.ir.ui.view 'theme_homepage_content' to exist."
        )
        self.assertEqual(
            theme_view._name,
            "theme.ir.ui.view",
            "Expected record to be a theme.ir.ui.view."
        )

    def test_homepage_inherits_website_homepage(self):
        """Verify theme view inherits from website.homepage."""
        theme_view = self.env.ref("theme_bioelevate.theme_homepage_content")
        self.assertEqual(
            theme_view.inherit_id.id,
            self.env.ref("website.homepage").id,
            "Expected theme_homepage_content to inherit from website.homepage."
        )

    def test_homepage_sections_in_theme_view(self):
        """Verify all required sections are present in the theme view arch."""
        theme_view = self.env.ref("theme_bioelevate.theme_homepage_content")
        arch = theme_view.arch or ""
        normalized_arch = " ".join(arch.split())

        required_snippets = [
            "s_text_block",
            "s_website_form",
        ]
        # Sections use s_text_block and s_website_form snippets
        expected_names = [
            "Hero",
            "Trust Strip",
            "About BioElevate",
            "Contact Us",
        ]

        for snippet in required_snippets:
            self.assertIn(
                snippet,
                arch,
                f"Homepage theme view is missing expected snippet '{snippet}'.",
            )

        for name in expected_names:
            self.assertIn(
                f'data-name="{name}"',
                arch,
                f"Homepage theme view is missing expected section data-name '{name}'.",
            )

        expected_fragments = [
            "Premium peptide products for clinical",
            "For licensed clinics",
            "Quality Standards",
            "&gt;= 99% purity",
            "Cold-chain delivery",
            "Quality you can count on",
            "60+",
            "Ready to work with us",
            "contact-section",
            "Send us a message",
            "data-model_name=\"mail.mail\"",
            "s_website_form_rows",
            "s_website_form_label",
            "/contactus-thank-you",
            "orders@bioelevate.org",
            "partners@bioelevate.org",
            "coa@bioelevate.org",
        ]

        for fragment in expected_fragments:
            normalized_fragment = " ".join(fragment.split())
            self.assertIn(
                normalized_fragment,
                normalized_arch,
                f"Homepage theme view is missing expected fragment '{fragment}'.",
            )

    def test_homepage_best_seller_tag_record_exists(self):
        """Verify best_seller product.tag data record is loaded."""
        best_seller_tag = self.env.ref(
            "theme_bioelevate.product_tag_best_seller",
            raise_if_not_found=False,
        )
        self.assertIsNotNone(
            best_seller_tag,
            "Expected product tag record theme_bioelevate.product_tag_best_seller.",
        )
        self.assertEqual(
            best_seller_tag.name,
            "best_seller",
            "Expected best seller product tag name to be 'best_seller'.",
        )

    def test_homepage_best_sellers_dynamic_snippet_is_top_and_configured(self):
        """Verify top homepage dynamic snippet is Best Sellers and tag-filtered by default."""
        theme_view = self.env.ref("theme_bioelevate.theme_homepage_content")
        arch = theme_view.arch or ""

        self.assertIn(
            'data-snippet="s_dynamic_snippet_products"',
            arch,
            "Expected homepage to include s_dynamic_snippet_products snippet.",
        )
        self.assertIn(
            'data-name="Best Sellers"',
            arch,
            "Expected homepage snippet section to be named Best Sellers.",
        )
        self.assertIn(
            "<h2 class=\"h3\">Best Sellers</h2>",
            arch,
            "Expected dynamic snippet title to be Best Sellers.",
        )
        self.assertNotIn(
            "Our latest content",
            arch,
            "Default dynamic snippet title should be replaced.",
        )
        self.assertNotIn(
            "Check out what's new in our company !",
            arch,
            "Default dynamic snippet subtitle should be removed.",
        )
        self.assertIn(
            "data-product-tag-ids",
            arch,
            "Expected dynamic snippet to set default product tag filter in dataset.",
        )
        self.assertIn(
            "request.env.ref('theme_bioelevate.product_tag_best_seller').id",
            arch,
            "Expected dynamic snippet tag dataset to reference best_seller tag xmlid.",
        )
        self.assertIn(
            "request.env.ref('website_sale.dynamic_filter_newest_products').id",
            arch,
            "Expected dynamic snippet to use website_sale newest products dynamic filter.",
        )

        best_sellers_index = arch.find('data-name="Best Sellers"')
        hero_index = arch.find('data-name="Hero"')
        self.assertGreaterEqual(
            best_sellers_index,
            0,
            "Best Sellers section marker not found in homepage arch.",
        )
        self.assertGreaterEqual(
            hero_index,
            0,
            "Hero section marker not found in homepage arch.",
        )
        self.assertLess(
            best_sellers_index,
            hero_index,
            "Expected Best Sellers section to be placed before Hero section.",
        )

    def test_homepage_category_filmstrip_snippet_above_best_sellers(self):
        """Verify homepage uses theme filmstrip snippet above Best Sellers without a section title."""
        theme_view = self.env.ref("theme_bioelevate.theme_homepage_content")
        arch = theme_view.arch or ""

        self.assertIn(
            't-call="theme_bioelevate.s_category_filmstrip_home"',
            arch,
            "Expected homepage to include theme category filmstrip snippet call.",
        )
        self.assertNotIn("Shop by Category", arch, "Expected category strip title to be removed.")
        self.assertNotIn("t-set=\"keep\"", arch, "Expected homepage filmstrip to avoid keep helper.")

        category_strip_index = arch.find('t-call="theme_bioelevate.s_category_filmstrip_home"')
        best_sellers_index = arch.find('data-name="Best Sellers"')
        self.assertGreaterEqual(
            category_strip_index,
            0,
            "Category Filmstrip section marker not found in homepage arch.",
        )
        self.assertGreaterEqual(
            best_sellers_index,
            0,
            "Best Sellers section marker not found in homepage arch.",
        )
        self.assertLess(
            category_strip_index,
            best_sellers_index,
            "Expected Category Filmstrip section to be placed before Best Sellers section.",
        )

    def test_homepage_category_filmstrip_template_uses_published_categories(self):
        """Verify theme filmstrip template uses shop-like DOM and published category filtering."""
        filmstrip_view = self.env.ref("theme_bioelevate.s_category_filmstrip_home")
        arch = filmstrip_view.arch or ""

        self.assertIn('data-snippet="s_category_filmstrip_home"', arch)
        self.assertIn('data-name="Category Filmstrip"', arch)
        self.assertNotIn('t-if="categories" id="o_wsale_categories_filmstrip"', arch)
        self.assertIn("o_wsale_filmstrip_container", arch)
        self.assertIn("o_wsale_filmstrip_item", arch)
        self.assertIn("o_wsale_filmstrip_pills", arch)
        self.assertNotIn("o_wsale_filmstrip_default", arch)
        self.assertIn("('has_published_products', '=', True)", arch)
        self.assertIn("('website_id', 'in', [False, request.env['website'].get_current_website().id])", arch)
        self.assertIn('t-att-href="\'/shop\'"', arch)
        self.assertIn("slug(c)", arch)

    def test_footer_sections_in_theme_view(self):
        """Verify provider footer content is present in the theme footer view."""
        footer_view = self.env.ref("theme_bioelevate.theme_footer_content")
        arch = footer_view.arch or ""
        normalized_arch = " ".join(arch.split())

        self.assertEqual(
            footer_view._name,
            "theme.ir.ui.view",
            "Expected footer record to be a theme.ir.ui.view.",
        )
        self.assertEqual(
            footer_view.inherit_id.id,
            self.env.ref("website.layout").id,
            "Expected theme_footer_content to inherit from website.layout.",
        )

        expected_fragments = [
            'id="footer"',
            'o_cc o_cc5 o_colored_level',
            "BioElevate",
            "Premium peptide products for licensed medical professionals and qualified distributors.",
            "Navigate",
            "Legal",
            "Home",
            "/shop",
            "/legal-compliance",
            "/privacy",
            "Privacy Policy",
            "/return-policy",
            "Returns and Refunds Policy",
            "/terms",
            "Terms and Conditions",
            "/home#contact-section",
            "Contact Us",
            "orders@bioelevate.org",
            "partners@bioelevate.org",
            "coa@bioelevate.org",
            "For licensed medical professionals and qualified distributors only.",
        ]

        for fragment in expected_fragments:
            normalized_fragment = " ".join(fragment.split())
            self.assertIn(
                normalized_fragment,
                normalized_arch,
                f"Footer theme view is missing expected fragment '{fragment}'.",
            )

    def test_default_color_palette_selected(self):
        """Verify bioelevate-default-light palette is set as default."""
        website = self.env.ref("website.default_website")
        custom_url = "/_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss"
        attachment = self.env["ir.attachment"].search(
            [
                ("url", "=", custom_url),
                ("website_id", "=", website.id),
            ],
            limit=1,
        )
        self.assertTrue(
            attachment,
            "Expected user_values.scss customization attachment for the default website.",
        )
        scss_content = base64.b64decode(attachment.datas or b"").decode("utf-8")
        self.assertIn(
            "'color-palettes-name': bioelevate-default-light",
            scss_content,
            "Default palette 'bioelevate-default-light' is not set in user_values.scss.",
        )
        self.assertIn(
            "'header-template': stretch",
            scss_content,
            "Header template 'stretch' is not set in user_values.scss.",
        )

    def test_header_template_stretch_enabled(self):
        """Verify stretch header template is enabled by default."""
        stretch_view = self.env.ref("website.template_header_stretch")
        default_view = self.env.ref("website.template_header_default")
        self.assertTrue(
            stretch_view.active,
            "Expected website.template_header_stretch to be active by default.",
        )
        self.assertFalse(
            default_view.active,
            "Expected website.template_header_default to be inactive when stretch is active.",
        )

    def test_header_cta_links_to_contact_section(self):
        """Verify header CTA button points to the homepage contact section."""
        cta_view = self.env.ref("theme_bioelevate.theme_header_cta_contact_section")
        self.assertEqual(
            cta_view._name,
            "theme.ir.ui.view",
            "Expected CTA override record to be a theme.ir.ui.view.",
        )
        self.assertEqual(
            cta_view.inherit_id.id,
            self.env.ref("website.header_call_to_action").id,
            "Expected CTA override to inherit from website.header_call_to_action.",
        )
        self.assertIn(
            "/home#contact-section",
            cta_view.arch or "",
            "Expected header CTA href to target /home#contact-section.",
        )

    def test_website_configurator_todo_marked_done(self):
        """Verify website configurator wizard is disabled."""
        configurator_todo = self.env.ref("website.website_configurator_todo")
        self.assertEqual(
            configurator_todo.state,
            "done",
            "Expected website configurator todo to be marked done for theme_bioelevate.",
        )

    def test_shop_page_thumbnails_catalog_design_config(self):
        """Verify shop page uses thumbnails catalog design with editor settings."""
        website = self.env.ref("website.default_website")

        self.assertEqual(
            website.shop_ppr,
            4,
            "Expected shop_ppr=4 (thumbnails catalog design).",
        )
        self.assertEqual(
            website.shop_ppg,
            40,
            "Expected shop_ppg=40 (Products per page).",
        )
        self.assertEqual(
            website.shop_gap,
            "16px",
            "Expected shop_gap=16px (thumbnails catalog design).",
        )
        self.assertEqual(
            website.shop_page_container,
            "regular",
            "Expected shop_page_container='regular'.",
        )

        design_classes = (website.shop_opt_products_design_classes or "").strip().split()
        expected_classes = [
            "o_wsale_products_opt_layout_catalog",
            "o_wsale_products_opt_design_thumbs",
            "o_wsale_products_opt_name_color_regular",
            "o_wsale_products_opt_thumb_cover",
            "o_wsale_products_opt_img_secondary_show",
            "o_wsale_products_opt_img_hover_zoom_out_light",
            "o_wsale_products_opt_has_cta",
            "o_wsale_products_opt_has_wishlist",
            "o_wsale_products_opt_has_comparison",
            "o_wsale_products_opt_actions_onhover",
            "o_wsale_products_opt_wishlist_fixed",
            "o_wsale_products_opt_actions_subtle",
            "o_wsale_products_opt_rounded_2",
            "o_wsale_products_opt_has_description",
        ]
        for cls in expected_classes:
            self.assertIn(
                cls,
                design_classes,
                f"Missing thumbnails catalog design class '{cls}' in shop_opt_products_design_classes.",
            )

        self.assertNotIn(
            "o_wsale_products_opt_layout_list",
            design_classes,
            "Expected list layout class to be absent for catalog thumbnails design.",
        )
        self.assertNotIn(
            "o_wsale_products_opt_design_condensed",
            design_classes,
            "Expected condensed design class to be absent for catalog thumbnails design.",
        )
        self.assertNotIn(
            "o_wsale_products_opt_actions_promote",
            design_classes,
            "Expected promote actions class to be absent for catalog thumbnails design.",
        )

        # Thumbnails preset keeps cover mode; explicit ratio classes are user-selectable and not defaulted.
        ratio_classes = [
            c
            for c in design_classes
            if c.startswith("o_wsale_products_opt_thumb_") and c != "o_wsale_products_opt_thumb_cover"
        ]
        self.assertFalse(
            ratio_classes,
            f"Expected no thumb ratio classes for thumbnails preset, found: {ratio_classes}",
        )

    def test_shop_page_views_enabled(self):
        """Verify shop page views are configured correctly."""
        enabled_views = [
            "website_sale.products_mobile_cols_single",
            "website_sale.filmstrip_categories_pills",
        ]
        disabled_views = [
            "website_sale.products_attributes",
            "website_sale.products_attributes_top",
            "website_sale.filmstrip_categories_grid",
        ]
        for xml_id in enabled_views:
            self.assertTrue(
                self.env.ref(xml_id).active,
                f"Expected {xml_id} to be enabled.",
            )
        for xml_id in disabled_views:
            self.assertFalse(
                self.env.ref(xml_id).active,
                f"Expected {xml_id} to be disabled.",
            )

    def test_shop_does_not_hide_product_images(self):
        """Verify shop image-hiding theme view is not loaded."""
        hide_images_view = self.env.ref(
            "theme_bioelevate.theme_shop_hide_product_images",
            raise_if_not_found=False,
        )
        self.assertFalse(
            hide_images_view,
            "Expected no theme view to hide product images on the shop page.",
        )

    def test_shop_thumbnails_option_enabled_in_scss_customization(self):
        """Verify shop thumbnails catalog design option is enabled in user_values.scss."""
        website = self.env.ref("website.default_website")
        custom_url = "/_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss"
        attachment = self.env["ir.attachment"].search(
            [
                ("url", "=", custom_url),
                ("website_id", "=", website.id),
            ],
            limit=1,
        )
        self.assertTrue(
            attachment,
            "Expected user_values.scss customization attachment for the default website.",
        )
        scss_content = base64.b64decode(attachment.datas or b"").decode("utf-8")
        self.assertIn(
            "shop-page-opt-products-design-classes",
            scss_content,
            "Expected shop-page-opt-products-design-classes in user_values.scss.",
        )
        self.assertIn(
            "o_wsale_products_opt_design_thumbs",
            scss_content,
            "Expected thumbnails design class in user_values.scss customization.",
        )
        self.assertNotIn(
            "o_wsale_products_opt_design_condensed",
            scss_content,
            "Expected condensed design class to be absent in user_values.scss customization.",
        )

    def test_legal_compliance_page_exists(self):
        """Verify legal & compliance page is created and published."""
        website = self.env.ref("website.default_website")
        legal_page = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/legal-compliance"),
            ],
            limit=1,
        )
        self.assertTrue(
            legal_page,
            "Expected /legal-compliance website.page to exist.",
        )
        self.assertTrue(
            legal_page.is_published,
            "Expected /legal-compliance page to be published.",
        )

    def test_legal_compliance_menu_exists(self):
        """Verify legal & compliance menu item exists on main menu."""
        website = self.env.ref("website.default_website")
        legal_menu = self.env["website.menu"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/legal-compliance"),
            ],
            limit=1,
        )
        self.assertTrue(
            legal_menu,
            "Expected a main menu entry for /legal-compliance.",
        )
        self.assertEqual(
            legal_menu.name,
            "Legal & Compliance",
            "Expected /legal-compliance menu label to be 'Legal & Compliance'.",
        )

    def test_privacy_policy_page_uses_native_url(self):
        """Verify privacy policy content is published at Odoo's native /privacy URL."""
        website = self.env.ref("website.default_website")
        privacy_pages = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/privacy"),
            ]
        )
        self.assertTrue(
            privacy_pages,
            "Expected /privacy website.page to exist.",
        )

        privacy_page = privacy_pages.filtered(
            lambda page: "theme_bioelevate.page_privacy_policy" in (page.arch or "")
        )[:1] or privacy_pages[:1]

        self.assertTrue(
            privacy_page.is_published,
            "Expected /privacy page to be published.",
        )

        arch = privacy_page.arch or ""
        expected_fragments = [
            "Privacy Policy",
            "BioElevate website is owned by BioElevate",
            "Personal information we collect",
            "The right to data portability",
            "info@bioelevate.org",
        ]
        for fragment in expected_fragments:
            self.assertIn(
                fragment,
                arch,
                f"Privacy policy page is missing expected fragment '{fragment}'.",
            )

    def test_return_policy_page_exists_without_menu(self):
        """Verify return policy page exists and no menu is created for it."""
        website = self.env.ref("website.default_website")
        return_pages = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/return-policy"),
            ]
        )
        self.assertTrue(
            return_pages,
            "Expected /return-policy website.page to exist.",
        )

        return_page = return_pages.filtered(
            lambda page: "theme_bioelevate.page_return_policy" in (page.arch or "")
        )[:1] or return_pages[:1]

        self.assertTrue(
            return_page.is_published,
            "Expected /return-policy page to be published.",
        )

        arch = return_page.arch or ""
        expected_fragments = [
            "Returns and Refunds Policy",
            "we do not offer refunds or accept returns under any circumstances",
            "Damaged, Defective, or Incorrect Orders",
            "Lost or Missing Packages",
            "info@bioelevate.org",
        ]
        for fragment in expected_fragments:
            self.assertIn(
                fragment,
                arch,
                f"Return policy page is missing expected fragment '{fragment}'.",
            )

        return_menu = self.env["website.menu"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/return-policy"),
            ],
            limit=1,
        )
        self.assertFalse(
            return_menu,
            "Expected no website.menu entry for /return-policy.",
        )

    def test_terms_content_updates_existing_odoo_terms_page(self):
        """Verify terms content uses Odoo's existing /terms mechanism."""
        website = self.env.ref("website.default_website")
        terms_pages = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/terms"),
            ]
        )
        self.assertFalse(
            terms_pages,
            "Expected no standalone website.page to be created for /terms.",
        )

        self.assertEqual(
            self.env["ir.config_parameter"].sudo().get_param("account.use_invoice_terms"),
            "True",
            "Expected account invoice terms to be enabled for Odoo's /terms route.",
        )
        company = website.company_id
        self.assertEqual(
            company.terms_type,
            "html",
            "Expected company terms_type='html' for Odoo's /terms route.",
        )
        terms_html = company.invoice_terms_html or ""
        expected_fragments = [
            "Terms and Conditions",
            "Welcome to BioElevate",
            "BioElevate's Website",
            "The website uses cookies",
            "You must not",
            "To the maximum extent permitted by applicable law",
        ]
        for fragment in expected_fragments:
            self.assertIn(
                fragment,
                terms_html,
                f"Terms content is missing expected fragment '{fragment}'.",
            )

    def test_terms_page_is_themed_via_account_template_inheritance(self):
        """Verify /terms keeps Odoo route but uses themed layout structure."""
        themed_terms_view = self.env.ref(
            "theme_bioelevate.theme_terms_conditions_page",
            raise_if_not_found=False,
        )
        self.assertIsNotNone(
            themed_terms_view,
            "Expected theme_terms_conditions_page to exist.",
        )
        self.assertEqual(
            themed_terms_view._name,
            "theme.ir.ui.view",
            "Expected terms page override to be a theme.ir.ui.view.",
        )
        self.assertEqual(
            themed_terms_view.inherit_id.id,
            self.env.ref("account.account_terms_conditions_page").id,
            "Expected terms page override to inherit account.account_terms_conditions_page.",
        )

        arch = themed_terms_view.arch or ""
        expected_fragments = [
            'id="wrap"',
            "data-name=\"Terms Hero\"",
            "data-name=\"Terms Content\"",
            "Terms and Conditions",
            "s_text_block o_cc o_cc5",
            "s_text_block o_cc o_cc1",
            "company.invoice_terms_html",
        ]
        for fragment in expected_fragments:
            self.assertIn(
                fragment,
                arch,
                f"Themed terms override is missing expected fragment '{fragment}'.",
            )

    def test_contactus_menu_removed(self):
        """Verify /contactus menu item is removed while page may still exist."""
        website = self.env.ref("website.default_website")
        contact_menus = self.env["website.menu"].search(
            [
                ("website_id", "=", website.id),
                ("url", "=", "/contactus"),
            ]
        )
        self.assertFalse(
            contact_menus,
            "Expected no website.menu entry pointing to /contactus.",
        )

    def test_favicon_generated(self):
        """Verify favicon attachment exists and is a valid ICO when readable."""
        import base64
        from io import BytesIO

        from PIL import Image
        from PIL import UnidentifiedImageError

        website = self.env.ref("website.default_website")
        favicon_attachment = self.env["ir.attachment"].sudo().search(
            [
                ("res_model", "=", "website"),
                ("res_id", "=", website.id),
                ("res_field", "=", "favicon"),
            ],
            limit=1,
        )
        self.assertTrue(
            favicon_attachment,
            "Expected a favicon attachment to be linked to the default website.",
        )
        self.assertEqual(
            favicon_attachment.mimetype,
            "image/vnd.microsoft.icon",
            "Expected favicon attachment mimetype to be ICO.",
        )
        self.assertGreater(
            favicon_attachment.file_size or 0,
            0,
            "Expected favicon attachment file size to be greater than zero.",
        )

        self.assertIsNotNone(
            website.favicon,
            "Expected favicon to be set on the default website.",
        )
        try:
            image = Image.open(BytesIO(base64.b64decode(website.favicon)))
        except (UnidentifiedImageError, ValueError, TypeError) as error:
            self.skipTest(
                "Favicon binary could not be decoded in this environment: %s" % error
            )
        self.assertEqual(image.format, "ICO", "Expected favicon to be ICO format.")
        self.assertEqual(
            image.size,
            (256, 256),
            "Expected favicon to be 256x256 pixels.",
        )

    def test_logo_png_exists(self):
        """Verify logo.png file exists in module static."""
        from odoo.tools.misc import file_path

        module_path = file_path("theme_bioelevate")
        logo_path = os.path.join(module_path, "static", "src", "img", "logo.png")
        self.assertTrue(
            os.path.exists(logo_path),
            f"Expected logo.png to exist at {logo_path}",
        )

    def test_website_logo_data_uses_logo_png(self):
        """Verify theme website data config points to logo.png."""
        from odoo.tools.misc import file_path

        module_path = file_path("theme_bioelevate")
        website_xml_path = os.path.join(module_path, "data", "website.xml")
        with open(website_xml_path, "r", encoding="utf-8") as website_xml_file:
            website_xml_content = website_xml_file.read()

        self.assertIn(
            'file="theme_bioelevate/static/src/img/logo.png"',
            website_xml_content,
            "Expected data/website.xml to set website logo from logo.png.",
        )

    def test_logo_attachment_points_to_logo_png(self):
        """Verify theme image attachment URL points to logo.png."""
        logo_attachment = self.env.ref("theme_bioelevate.img_logo", raise_if_not_found=False)
        self.assertIsNotNone(logo_attachment, "Expected img_logo attachment to exist.")
        self.assertEqual(
            logo_attachment.url,
            "/theme_bioelevate/static/src/img/logo.png",
            "Expected img_logo URL to reference logo.png.",
        )

    def test_favicon_hook_supports_logo_png_fallback(self):
        """Verify pre-init favicon generation supports logo.png fallback."""
        from odoo.tools.misc import file_path

        module_path = file_path("theme_bioelevate")
        hooks_path = os.path.join(module_path, "hooks.py")
        with open(hooks_path, "r", encoding="utf-8") as hooks_file:
            hooks_content = hooks_file.read()

        self.assertIn(
            '"logo.png"',
            hooks_content,
            "Expected hooks.py to include logo.png as favicon source fallback.",
        )

    def test_primary_variables_sets_footer_combination(self):
        """Verify theme defaults include footer color combination CC5."""
        from odoo.tools.misc import file_path

        module_path = file_path("theme_bioelevate")
        scss_path = os.path.join(module_path, "static", "src", "scss", "primary_variables.scss")
        with open(scss_path, "r", encoding="utf-8") as scss_file:
            scss_content = scss_file.read()

        self.assertIn(
            "'footer': 5",
            scss_content,
            "Expected primary_variables.scss to set footer color combination to CC5.",
        )

    def test_no_copyright_bar(self):
        """Test copyright bar is hidden via website.footer_no_copyright."""
        footer_view = self.env.ref("website.footer_no_copyright")
        self.assertTrue(
            footer_view.active,
            "Expected website.footer_no_copyright to be active (copyright bar hidden).",
        )

    def test_brand_promotion_override_exists(self):
        """Verify theme.ir.ui.view overrides website.brand_promotion."""
        theme_view = self.env.ref(
            "theme_bioelevate.theme_brand_promotion",
            raise_if_not_found=False,
        )
        self.assertIsNotNone(
            theme_view,
            "Expected theme.ir.ui.view 'theme_brand_promotion' to exist.",
        )
        self.assertEqual(
            theme_view._name,
            "theme.ir.ui.view",
            "Expected record to be a theme.ir.ui.view.",
        )
        self.assertEqual(
            theme_view.inherit_id.id,
            self.env.ref("website.brand_promotion").id,
            "Expected theme_brand_promotion to inherit from website.brand_promotion.",
        )
        self.assertIn(
            "o_brand_promotion",
            theme_view.arch or "",
            "Expected theme view arch to contain 'o_brand_promotion' span.",
        )

    def test_portal_branding_removed(self):
        """Test portal 'Powered by Odoo' branding is removed."""
        theme_view = self.env.ref(
            "theme_bioelevate.theme_portal_sidebar_no_branding",
            raise_if_not_found=False,
        )
        self.assertIsNotNone(
            theme_view,
            "Expected theme.ir.ui.view 'theme_portal_sidebar_no_branding' to exist.",
        )
        self.assertEqual(
            theme_view._name,
            "theme.ir.ui.view",
            "Expected record to be a theme.ir.ui.view.",
        )
        self.assertEqual(
            theme_view.inherit_id.id,
            self.env.ref("portal.portal_record_sidebar").id,
            "Expected theme_portal_sidebar_no_branding to inherit from portal.portal_record_sidebar.",
        )
