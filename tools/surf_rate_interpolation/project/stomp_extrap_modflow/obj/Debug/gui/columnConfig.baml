   M S B A M L   `   `   `  ����X  Tsurf_rate_interp_win_intel_64, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null;"clr-namespace:surf_rate_interp.guisurf_rate_interp.gui  5      '    !surf_rate_interp.gui.columnConfig   5      W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5      R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5      Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     5      @d2http://schemas.microsoft.com/expression/blend/2008     5      4local"clr-namespace:surf_rate_interp.gui     5        N� Title$  columnSetting��5	      .��5
      �  � ColumnDefinitions 5   
   �� 5      $��* �6   6+    � RowDefinitions 5   
   �� 5      $��* �6   6)   .+�5   
   &   System.Windows.Controls.DataGrid  -   5          Name$ auGrid��5   �   $��0��6   $��0��6#   $��Stretch=�60   $��Stretch=�6L      AutoGenerateColumns .  ��6j   ��    Columns 5      0  *System.Windows.Controls.DataGridTextColumn  5      ,  &System.Windows.Controls.DataGridColumn   
IsReadOnly . -   5        col0��   Header$
 File��5   E      Width5  /System.Windows.Controls.DataGridLengthConverter$ * 6l   1  +System.Windows.Controls.DataGridBoundColumn	   Binding	 6S   �� *file+
   ElementStyle
 5      �� 5      .�5      ��  �� Property � �� �� Value$
 Wrap=�6G   �� 5       �@��TextAlignment$
 Left=�6H   5      5      4  .System.Windows.Controls.DataGridCheckBoxColumn  5       . -   5        col1��$
 Done��5   I   $ 50 6u      MaxWidth$ 50Q�6�   	 6W   �� *	processed+6�   5      5!      5"      