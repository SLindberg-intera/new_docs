   M S B A M L   `   `   `  ���� O  Kstomp_extrap_modflow, Version=1.0.0.0, Culture=neutral, PublicKeyToken=nullC&clr-namespace:stomp_extrap_modflow.guistomp_extrap_modflow.gui  ,    &stomp_extrap_modflow.gui.columnSetting   W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     @d2http://schemas.microsoft.com/expression/blend/2008     8local&clr-namespace:stomp_extrap_modflow.gui       N� Title$  columnSetting��.���  � ColumnDefinitions �� $��* � � RowDefinitions �� $��20 ��� $��* �.+��� -    ��Name$ button��$��0��$��0��$
��help��$
��Left=�$��Stretch=�$��75��&   System.Windows.Controls.DataGrid  -     Name$ auGrid��$��0��$��1��$��Stretch=�$��Stretch=�   AutoGenerateColumns .  ����    Columns 0  *System.Windows.Controls.DataGridTextColumn  ,  &System.Windows.Controls.DataGridColumn   
IsReadOnly . -   col1��   Header$ Column��	   MinWidth$	 50Q�
   MaxWidth$
 50Q�1  +System.Windows.Controls.DataGridBoundColumn   Binding �� *
column_num+   ElementStyle �� .���  �� Property � �� �� Value$
 Wrap=���  �@��TextAlignment$
 Left=�4  .System.Windows.Controls.DataGridCheckBoxColumn  -   col2��$
 Time��   Width5  /System.Windows.Controls.DataGridLengthConverter$ 50 $
 50Q� �� *time+   . -   col3��$ title��$ *  �� *title+ �� .���  � ��$
 Wrap=���  �@��TextAlignment$
 Left=�   .  -   col4��$ 
definition��$	 100  �� *
definition+ �� .���  � ��$
 Wrap=���  �@��TextAlignment$
 Left=�4   .stomp_extrap_modflow.gui.DataGriddecimalColumn   .  -   col5��$ Conv. F.��$ 50 $
 50Q� �� *conv_factor+