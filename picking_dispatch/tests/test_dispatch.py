from openerp.tests.common import TransactionCase


class TestPickingDispatch(TransactionCase):

    def setUp(self):
        super(TestPickingDispatch, self).setUp()
        env = self.env
        ref = self.ref
        dispatch_obj = env['picking.dispatch']
        stock_loc_id = ref('stock.stock_location_stock')
        customers_loc_id = ref('stock.stock_location_customers')
        pick = env['stock.picking.out'].create(
            {'type': 'out',
             'location_dest_id': customers_loc_id,
             'move_lines': [
                 (0, 0, {'name': 'move1',
                         'product_id': ref('product.product_product_6'),
                         'product_uom': ref('product.product_uom_unit'),
                         'product_qty': 1,
                         'location_id': stock_loc_id,
                         'location_dest_id': customers_loc_id,
                         }
                  ),
                 (0, 0, {'name': 'move2',
                         'product_id': ref('product.product_product_7'),
                         'product_uom': ref('product.product_uom_unit'),
                         'product_qty': 1,
                         'location_id': stock_loc_id,
                         'location_dest_id': customers_loc_id,
                         }
                  ),
                 ]
             })
        pick.signal_workflow('button_confirm')
        disp = dispatch_obj.create({'move_ids': [(4, line.id)
                                                 for line in pick.move_lines]})
        self.picking = pick
        self.dispatch = disp

    def test_related_picking(self):
        picking_ids = [pick.id for pick in self.dispatch.related_picking_ids]
        self.assertEqual(picking_ids, [self.picking.id])
        self.assertEqual(self.picking.state, 'confirmed')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'confirmed')

    def test_assign(self):
        self.dispatch.write({'picker_id': self.ref('base.user_demo'),
                             })
        self.dispatch.action_assign()
        self.assertEqual(self.dispatch.state, 'assigned')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'confirmed')

    def test_assign_moves(self):
        self.dispatch.check_assign_all()
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'assigned')

    def test_cancel(self):
        self.dispatch.action_cancel()
        self.assertEqual(self.dispatch.state, 'cancel')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'cancel')
        self.assertEqual(self.picking.state, 'cancel')

    def test_done(self):
        self.test_assign()
        for move in self.picking.move_lines:
            move.action_done()
        self.assertEqual(self.picking.state, 'done')
        for move in self.picking.move_lines:
            move.refresh()
            self.assertEqual(move.state, 'done')
        self.dispatch.refresh()
        self.assertEqual(self.dispatch.state, 'done')
