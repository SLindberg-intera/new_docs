   M S B A M L   `   `   `  ���� X  Tsurf_rate_interp_win_intel_64, Version=1.0.0.0, Culture=neutral, PublicKeyToken=nullC&clr-namespace:stomp_extrap_modflow.guistomp_extrap_modflow.gui  +    %stomp_extrap_modflow.gui.gridSettings   W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     @d2http://schemas.microsoft.com/expression/blend/2008     8local&clr-namespace:stomp_extrap_modflow.gui       N� Title$  gridSettings��.���  � ColumnDefinitions �� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��50 ��� $��* � � RowDefinitions �� $��25 ��� $��* �.+��� -    ��Name$ button��$��0��$��0��$
��help��$��stretch=�$��Stretch=��� -    ��Name$ label4��$��1��$��1��$��5��$��0��$��
Start(yr):��$��Center=�$��Right=�$��Stretch=�$��Stretch=��� -    ��Name$ tb_startYear��$��1��$��1��$��6��$��0��$��Stretch=� �� TextWrapping$ NoWrap=�$�� ��$��Stretch=��� -   $ label5��$��1��$��1��$��7��$��0��$
��End:��$��Center=�$��Right=�$��Stretch=�$��Stretch=��� -   $ 
tb_endYear��$��1��$��1��$��8��$��0��$��Stretch=�$ NoWrap=�$�� ��$��Stretch=�&   System.Windows.Controls.DataGrid  -     Name$ auGrid��$��9��$��1��$��0��$��1��$��Stretch=�$��Stretch=�   AutoGenerateColumns .  ���� 	   Columns	 4  .System.Windows.Controls.DataGridCheckBoxColumn  -   col0��,  &System.Windows.Controls.DataGridColumn
   Header$

 Time��   Width5  /System.Windows.Controls.DataGridLengthConverter$ 50    MaxWidth$ 50Q�1  +System.Windows.Controls.DataGridBoundColumn   Binding �� *time+0  *System.Windows.Controls.DataGridTextColumn     
IsReadOnly . -   col1��$

 Name��$ *  �� *name+   ElementStyle �� .���  �� Property � �� �� Value$
 Wrap=���  �@��TextAlignment$
 Left=�   .  -	   col2��$
 i��$ 50  �� *i+ �� .���  � ��$
 Wrap=���  �@��TextAlignment$
 Left=�   .  -
   col3��$
 j��$ 50  �� *j+ �� .���  � ��$
 Wrap=���  �@��TextAlignment$
 Left=�   .  -   col4��$
 K��$ 50  �� *k+ �� .���  � ��$
 Wrap=���  �@��TextAlignment$
 Left=�