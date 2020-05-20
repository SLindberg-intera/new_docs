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
using Microsoft.WindowsAPICodePack.Dialogs;
using System.Text.RegularExpressions;
using Microsoft.Win32;
using stomp_extrap_modflow.framework;
using stomp_extrap_modflow.utility;
namespace stomp_extrap_modflow.gui
{
    /// <summary>
    /// Interaction logic for buildHSS.xaml
    /// </summary>
    public partial class buildHSS : Page
    {
        private string[] files;
        //private Dictionary<int, decimal[]> data;
        private string path = "";
        private bool consolidated_file = false;
        private gridSettings grid = new gridSettings();
        private char delim = '\t';
        public buildHSS()
        {
            InitializeComponent();
            winFrame.Content = grid;

        }
        private void load_file(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openfiledialog1 = new OpenFileDialog();
            //openfiledialog1.InitialDirectory = dir;
            openfiledialog1.Filter = "dat (*.dat)|*.dat|All Files (*.*)|*.*";
            openfiledialog1.FilterIndex = 1;
            openfiledialog1.Multiselect = true;
            openfiledialog1.RestoreDirectory = false;  //leave it where the files actually are for reading the raw data files (03-27-2012)

            openfiledialog1.Title = "Select file(s) to be processed:";

            openfiledialog1.ShowDialog();

            //path = System.IO.Path.GetDirectoryName(openfiledialog1.FileName) + "\\";
            files = openfiledialog1.FileNames;
            tb_fileName.Text = "";
            foreach (string file in files)
            {
                tb_fileName.Text += file;
            }
            hssp hss = new hssp();
            //hss.build_package_references(tb_templatedir.Text);
            foreach (string file in files)
            {
                hss.build_source_data(file, consolidated_file);
            }
            grid.file_def = hss.source;
            grid.refresh();
        }
        private void btn_buildHSS_Click(object sender, RoutedEventArgs e)
        {
            UiServices.SetBusyState();
            hssp hss = new hssp();
            hss.source = grid.file_def;
            
            if (path.Length > 1)
            {
                
                using (new WaitCursor())
                {
                    hss.build_package_references(tb_templatedir.Text);
                    hss.buildHSS(delim, grid.startYear, grid.endYear, path);
                }
            }
            else
            {
                MessageBox.Show("Invalid output folder", "Error");
            }
        }
        private void btn_templateDir_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openfiledialog1 = new OpenFileDialog();
            //openfiledialog1.InitialDirectory = dir;
            openfiledialog1.Filter = "dat (*.dat)|*.dat|All Files (*.*)|*.*";
            openfiledialog1.FilterIndex = 1;
            openfiledialog1.Multiselect = false;
            openfiledialog1.RestoreDirectory = false;  //leave it where the files actually are for reading the raw data files (03-27-2012)

            openfiledialog1.Title = "Select file(s) to be processed:";

            openfiledialog1.ShowDialog();

            //path = System.IO.Path.GetDirectoryName(openfiledialog1.FileName) + "\\";
            //files = openfiledialog1.FileNames;
            tb_templatedir.Text += openfiledialog1.FileName;

        }

        private void btn_outDir_Click(object sender, RoutedEventArgs e)
        {
            CommonOpenFileDialog dialog = new CommonOpenFileDialog();
            //dialog.InitialDirectory = "C:\\Users";
            dialog.IsFolderPicker = true;
            if (dialog.ShowDialog() == CommonFileDialogResult.Ok)
            {
                tb_outdir.Text = dialog.FileName;
                if(tb_outdir.Text.Substring(tb_outdir.Text.Length -1, 1) != "\\")
                {
                    tb_outdir.Text += "\\";
                }
            }
        }
        private void tb_templatedir_TextChanged(object sender, TextChangedEventArgs e)
        {
            //if (tb_templatedir.Text.Substring(tb_templatedir.Text.Length - 1, 1) != "\\")
            //{
            //    tb_templatedir.Text += "\\";
            //}
            //path = tb_templatedir.Text;
        }
        private void tb_outdir_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (tb_outdir.Text.Substring(tb_outdir.Text.Length - 1, 1) != "\\")
            {
                tb_outdir.Text += "\\";
            }
            path = tb_outdir.Text;
        }

        private void cb_consolidated_check(object sender, RoutedEventArgs e)
        {
            if(cb_consolidated.IsChecked == true)
            {
                consolidated_file = true;
            }
            else
            {
                consolidated_file = false;
            }
        }

    }
}
