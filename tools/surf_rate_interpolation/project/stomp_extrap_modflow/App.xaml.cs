using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
namespace stomp_extrap_modflow
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {

        private void Application_Startup(object sender, StartupEventArgs e)
        {
            MainWindow wnd;
            if (e.Args.Length == 1  && e.Args[0].Length > 0)
            {
                 wnd = new MainWindow(e.Args[0]);
            }
            else
            {
                wnd = new MainWindow();
            }
            wnd.Show();

        }
    }
}

