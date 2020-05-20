using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using stomp_extrap_modflow.data;
namespace stomp_extrap_modflow.gui
{
    /// <summary>
    /// Interaction logic for largeWindow.xaml
    /// </summary>
    public partial class largeWindow : Window
    {

        public largeWindow()
        {
            InitializeComponent();
        }
        public void load_col_setting(columnSetting page)
        {
            winFrame.Content = page;
        }

        private void btn_hide_Click(object sender, RoutedEventArgs e)
        {
            this.Hide();
        }
    }
}
