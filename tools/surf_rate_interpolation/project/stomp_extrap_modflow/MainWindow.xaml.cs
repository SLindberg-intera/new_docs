
//using Microsoft.Win32;
//using System;
//using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using System.Threading.Tasks;
using System.Windows;
//using System.Windows.Controls;
//using System.Windows.Data;
//using System.Windows.Documents;
//using System.Windows.Input;
//using System.Windows.Media;
//using System.Windows.Media.Imaging;
//using System.Windows.Navigation;
//using System.Windows.Shapes;
using surf_rate_interp.framework;
using stomp_extrap_modflow.gui;
using surf_rate_interp.gui;
//using stomp_extrap_modflow.data;
//using Microsoft.WindowsAPICodePack.Dialogs;
//using System.Text.RegularExpressions;
namespace stomp_extrap_modflow
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        //private largeWindow winFrame = new largeWindow();
        
        private Interpolate interp_win = new Interpolate();
        private buildHSS hss_win = new buildHSS();
        public MainWindow()
        {
            InitializeComponent();
            winFrame.Content = interp_win;
        }
        public MainWindow(string config)
        {
            InitializeComponent();
            menu.Visibility = Visibility.Hidden;
            config_interp config_interp = new config_interp(config);
            winFrame.Content = config_interp;
        }
        private void load_interpolate_page(object sender, RoutedEventArgs e)
        {
            winFrame.Content = interp_win;
        }
        private void load_hss_page(object sender, RoutedEventArgs e)
        {
            winFrame.Content = hss_win;
        }
        private void exit(object object_sender, RoutedEventArgs e)
        {
            System.Windows.Application.Current.Shutdown();
        }
    }
}

