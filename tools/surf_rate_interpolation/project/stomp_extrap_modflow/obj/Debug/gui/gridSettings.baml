   M S B A M L   `   `   `  ����X  Tsurf_rate_interp_win_intel_64, Version=1.0.0.0, Culture=neutral, PublicKeyToken=nullC&clr-namespace:stomp_extrap_modflow.guistomp_extrap_modflow.gui  5      +    %stomp_extrap_modflow.gui.gridSettings   5      W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5      R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5      Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     5      @d2http://schemas.microsoft.com/expression/blend/2008     5      8local&clr-namespace:stomp_extrap_modflow.gui     5        N� Title$  gridSettings��5      .��5
      �  � ColumnDefinitions 5   
   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��50 �6   6,   �� 5      $��* �6   6+    � RowDefinitions 5   
   �� 5      $��25 �6   6*   �� 5      $��* �6   6)   .+�5   
   �� -   5         ��Name$ button��5   .   $��0��6   $��0��6!   $
��help��6>   $��stretch=�6M   $��Stretch=�6k   6�   �� 5    
   -   5         ��Name$ label4��5    T   $��1��6   $��1��6%   $��5��66   $��0��6F   $��
Start(yr):��6d   $��Center=�6y   $��Right=�6�   $��Stretch=�6�   $��Stretch=�6�   �� 5!   
   -   5         ��Name$ tb_startYear��5!   T   $��1��6   $��1��6&   $��6��67   $��0��6G   $��Stretch=�6j    �� TextWrapping$ NoWrap=�6�   $�� ��6�   $��Stretch=�6�   6�   �� 5"   
   -   5        $ label5��5"   T   $��1��6   $��1��6%   $��7��66   $��0��6F   $
��End:��6d   $��Center=�6s   $��Right=�6�   $��Stretch=�6�   $��Stretch=�6�   �� 5#   
   -   5        $ 
tb_endYear��5#   T   $��1��6   $��1��6&   $��8��67   $��0��6G   $��Stretch=�6h   $ NoWrap=�6�   $�� ��6�   $��Stretch=�6�   6�   &   System.Windows.Controls.DataGrid  5$   
   -   5          Name$ auGrid��5$   �   $��9��6   $��1��6'   $��0��68   $��1��6H   $��Stretch=�6U   $��Stretch=�6q      AutoGenerateColumns .  ��6�   �� 	   Columns	 5%      4  .System.Windows.Controls.DataGridCheckBoxColumn  5&      -   5        col0��,  &System.Windows.Controls.DataGridColumn
   Header$

 Time��5&   8      Width5  /System.Windows.Controls.DataGridLengthConverter$ 50 6_      MaxWidth$ 50Q�6j   1  +System.Windows.Controls.DataGridBoundColumn   Binding 6F   �� *time+6j   0  *System.Windows.Controls.DataGridTextColumn  5'         
IsReadOnly . -   5        col1��$

 Name��5'   E   $ * 6l    6S   �� *name+   ElementStyle 5(      �� 5)      .�5*      ��  �� Property � �� �� Value$
 Wrap=�6G   �� 5+       �@��TextAlignment$
 Left=�6H   5,      5.        5/       .  -	   5        col2��$
 i��5/   F   $ 50 6g    6Q   �� *i+ 50      �� 51      .�52      ��  � ��$
 Wrap=�6G   �� 53       �@��TextAlignment$
 Left=�6H   54      56        57       .  -
   5        col3��$
 j��57   F   $ 50 6g    6Q   �� *j+ 58      �� 59      .�5:      ��  � ��$
 Wrap=�6G   �� 5;       �@��TextAlignment$
 Left=�6H   5<      5>        5?       .  -   5        col4��$
 K��5?   F   $ 50 6g    6Q   �� *k+ 5@      �� 5A      .�5B      ��  � ��$
 Wrap=�6G   �� 5C       �@��TextAlignment$
 Left=�6H   5D      5F      5H      5J      5K      