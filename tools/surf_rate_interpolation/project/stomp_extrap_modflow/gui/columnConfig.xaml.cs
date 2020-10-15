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
using System.Windows.Navigation;
using System.Windows.Shapes;
using stomp_extrap_modflow.data;
using surf_rate_interp.data;

namespace surf_rate_interp.gui
{
    /// <summary>
    /// Interaction logic for columnSetting.xaml
    /// </summary>
    public partial class columnConfig : Page
    {
        internal List<configCols> column_def;
        public columnConfig()
        {
            InitializeComponent();
            column_def = new List<configCols>();
            this.DataContext = column_def;
            //this.tb_instructions.Text = instructions;
        }
        public void refresh()
        {
            DataContext = column_def;
            auGrid.Items.Refresh();
        }
        
    }

}
