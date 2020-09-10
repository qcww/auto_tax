# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Dec  4 2019)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainMenu
###########################################################################

class MainMenu ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"税务数据更新与税款缴纳客户端", pos = wx.DefaultPosition, size = wx.Size( 500,392 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 500,392 ), wx.Size( 500,392 ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		self.menu_bar = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"清空本地任务", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.Append( self.m_menuItem1 )

		self.menu_bar.Append( self.m_menu1, u"操作" )

		self.setting_menu = wx.Menu()
		self.env_menu = wx.Menu()
		self.set_pro_menu = wx.MenuItem( self.env_menu, wx.ID_ANY, u"正式", wx.EmptyString, wx.ITEM_RADIO )
		self.env_menu.Append( self.set_pro_menu )

		self.set_test_menu = wx.MenuItem( self.env_menu, wx.ID_ANY, u"测试", wx.EmptyString, wx.ITEM_RADIO )
		self.env_menu.Append( self.set_test_menu )

		self.setting_menu.AppendSubMenu( self.env_menu, u"环境" )

		self.browser_menu = wx.Menu()
		self.set_bro_show_menu = wx.MenuItem( self.browser_menu, wx.ID_ANY, u"显示", wx.EmptyString, wx.ITEM_RADIO )
		self.browser_menu.Append( self.set_bro_show_menu )

		self.set_bro_hide_menu = wx.MenuItem( self.browser_menu, wx.ID_ANY, u"隐藏", wx.EmptyString, wx.ITEM_RADIO )
		self.browser_menu.Append( self.set_bro_hide_menu )

		self.setting_menu.AppendSubMenu( self.browser_menu, u"浏览器" )

		self.tax_menu = wx.Menu()
		self.set_tax_0 = wx.MenuItem( self.tax_menu, wx.ID_ANY, u"小规模无收入", wx.EmptyString, wx.ITEM_RADIO )
		self.tax_menu.Append( self.set_tax_0 )

		self.set_tax_1 = wx.MenuItem( self.tax_menu, wx.ID_ANY, u"小规模有收入", wx.EmptyString, wx.ITEM_RADIO )
		self.tax_menu.Append( self.set_tax_1 )

		self.set_tax_2 = wx.MenuItem( self.tax_menu, wx.ID_ANY, u"一般纳税人无收入", wx.EmptyString, wx.ITEM_RADIO )
		self.tax_menu.Append( self.set_tax_2 )

		self.set_tax_3 = wx.MenuItem( self.tax_menu, wx.ID_ANY, u"一般纳税人有收入", wx.EmptyString, wx.ITEM_RADIO )
		self.tax_menu.Append( self.set_tax_3 )

		self.set_tax_4 = wx.MenuItem( self.tax_menu, wx.ID_ANY, u"循环挂起", wx.EmptyString, wx.ITEM_RADIO )
		self.tax_menu.Append( self.set_tax_4 )

		self.setting_menu.AppendSubMenu( self.tax_menu, u"报税" )

		self.menu_bar.Append( self.setting_menu, u"设置" )

		self.SetMenuBar( self.menu_bar )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"任务" ), wx.VERTICAL )

		task_listChoices = []
		self.task_list = wx.ListBox( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( 365,120 ), task_listChoices, 0|wx.VSCROLL )
		sbSizer1.Add( self.task_list, 0, wx.ALL, 5 )


		bSizer5.Add( sbSizer1, 1, wx.EXPAND, 5 )

		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"日志" ), wx.VERTICAL )

		log_listChoices = []
		self.log_list = wx.ListBox( sbSizer4.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( 365,120 ), log_listChoices, 0|wx.VSCROLL )
		sbSizer4.Add( self.log_list, 0, wx.ALL, 5 )


		bSizer5.Add( sbSizer4, 1, wx.EXPAND, 5 )


		bSizer3.Add( bSizer5, 4, wx.EXPAND, 5 )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"操作" ), wx.VERTICAL )

		self.retry_btn = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"重试", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.retry_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.agent_btn = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"代开发票", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.agent_btn, 0, wx.ALL, 5 )

		self.report_btn = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"报税", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.report_btn, 0, wx.ALL, 5 )

		self.kk_btn = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"扣款", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.kk_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.tax_sb_btn = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"社保上传", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.tax_sb_btn, 0, wx.ALL, 5 )


		bSizer3.Add( sbSizer2, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer3 )
		self.Layout()
		self.status_bar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.clear_log, id = self.m_menuItem1.GetId() )
		self.Bind( wx.EVT_MENU, self.set_env_pro, id = self.set_pro_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.set_env_test, id = self.set_test_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.set_bro_show, id = self.set_bro_show_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.set_bro_hide, id = self.set_bro_hide_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.set_tax_0_0, id = self.set_tax_0.GetId() )
		self.Bind( wx.EVT_MENU, self.set_tax_0_1, id = self.set_tax_1.GetId() )
		self.Bind( wx.EVT_MENU, self.set_tax_1_0, id = self.set_tax_2.GetId() )
		self.Bind( wx.EVT_MENU, self.set_tax_1_1, id = self.set_tax_3.GetId() )
		self.Bind( wx.EVT_MENU, self.set_tax_all, id = self.set_tax_4.GetId() )
		self.retry_btn.Bind( wx.EVT_TOGGLEBUTTON, self.retry )
		self.agent_btn.Bind( wx.EVT_TOGGLEBUTTON, self.add_agent_task )
		self.report_btn.Bind( wx.EVT_TOGGLEBUTTON, self.add_auto_tax_task )
		self.kk_btn.Bind( wx.EVT_TOGGLEBUTTON, self.add_kk_task )
		self.tax_sb_btn.Bind( wx.EVT_TOGGLEBUTTON, self.add_sb_upload_task )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def clear_log( self, event ):
		event.Skip()

	def set_env_pro( self, event ):
		event.Skip()

	def set_env_test( self, event ):
		event.Skip()

	def set_bro_show( self, event ):
		event.Skip()

	def set_bro_hide( self, event ):
		event.Skip()

	def set_tax_0_0( self, event ):
		event.Skip()

	def set_tax_0_1( self, event ):
		event.Skip()

	def set_tax_1_0( self, event ):
		event.Skip()

	def set_tax_1_1( self, event ):
		event.Skip()

	def set_tax_all( self, event ):
		event.Skip()

	def retry( self, event ):
		event.Skip()

	def add_agent_task( self, event ):
		event.Skip()

	def add_auto_tax_task( self, event ):
		event.Skip()

	def add_kk_task( self, event ):
		event.Skip()

	def add_sb_upload_task( self, event ):
		event.Skip()


