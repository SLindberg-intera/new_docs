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
using System.Text.RegularExpressions;
namespace stomp_extrap_modflow.gui
{
    /// <summary>
    /// Interaction logic for gridSettings.xaml
    /// </summary>
    public partial class gridSettings : Page
    {
        public int MaxHSSSource = 0;
        public int MaxHSSCells = 0;
        public int startYear = 2018;
        public int endYear = 12017;
        internal List<hss_data_files> file_def;
        public gridSettings()
        {
            InitializeComponent();
            file_def = new List<hss_data_files>();
            this.DataContext = file_def;
            //tb_MaxHSSCells.Text = MaxHSSCells.ToString();
            //tb_MaxHSSSource.Text = MaxHSSSource.ToString();
            tb_startYear.Text = startYear.ToString();
            tb_endYear.Text = endYear.ToString();
        }
        public void refresh()
        {
            DataContext = file_def;
            auGrid.Items.Refresh();
            //calcHeader();
        }
        private string instructions =
@"
";

        private void button_Click(object sender, RoutedEventArgs e)
        {

            MessageBox.Show(instructions, "Info");
        }

        private void auGrid_CellEditEnding(object sender, DataGridCellEditEndingEventArgs e)
        {
            //calcHeader();

        }
        //public void calcHeader()
        //{
        //    MaxHSSSource = file_def.Where(f => f.i != null && f.i.Length > 0 && f.j != null && f.j.Length > 0).Select(f => new { i = f.i, j = f.j }).Distinct().Count();
        //    MaxHSSCells = MaxHSSSource;

        //    tb_MaxHSSSource.Text = MaxHSSSource.ToString();
        //    tb_MaxHSSCells.Text = MaxHSSCells.ToString();
        //}

        private void auGrid_SelectedCellsChanged(object sender, SelectedCellsChangedEventArgs e)
        {
            //calcHeader();
        }
        private static readonly Regex _regex = new Regex("[^0-9]+"); //regex that matches disallowed text
        private static bool IsTextAllowed(string text)
        {
            return !_regex.IsMatch(text);
        }

        private void check_numeric_input(object sender, TextCompositionEventArgs e)
        {
             e.Handled = _regex.IsMatch(e.Text);
            //e.Handled = !IsTextAllowed(e.Text);
            //e.Handled = Double.TryParse(e.Text, out startYear);
        }

        private void tb_startYear_TextChanged(object sender, TextChangedEventArgs e)
        {
            int.TryParse(tb_startYear.Text, out startYear);
        }

        private void tb_endYear_TextChanged(object sender, TextChangedEventArgs e)
        {
            int.TryParse(tb_endYear.Text, out endYear);
        }
    }
}
