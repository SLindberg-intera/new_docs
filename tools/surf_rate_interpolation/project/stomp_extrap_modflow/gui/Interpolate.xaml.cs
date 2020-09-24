using Microsoft.Win32;
using System;
using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
//using System.Windows.Data;
//using System.Windows.Documents;
using System.Windows.Input;
//using System.Windows.Media;
//using System.Windows.Media.Imaging;
//using System.Windows.Navigation;
//using System.Windows.Shapes;
using stomp_extrap_modflow.framework;
//using stomp_extrap_modflow.gui;
using stomp_extrap_modflow.data;
using Microsoft.WindowsAPICodePack.Dialogs;
using System.Text.RegularExpressions;
using surf_rate_interp.framework;

namespace stomp_extrap_modflow.gui
{
    /// <summary>
    /// Interaction logic for Interpolate.xaml
    /// </summary>
    public partial class Interpolate : Page
    {
        private columnSetting colSet = new columnSetting();
        public Interpolate()
        {
            InitializeComponent();
            winFrame.Content = colSet;
        }
        private string[] header1;
        private string[] header2;
        private string[] files;
        private char delim = ' ';
        //private Dictionary<int, decimal[]> data;
        private string path = "";
        //private List<columns> column_def;
        private void load_srf(object sender, RoutedEventArgs e)
        {            
            OpenFileDialog openfiledialog1 = new OpenFileDialog();
            process_srf srf = new process_srf();
            //openfiledialog1.InitialDirectory = dir;
            if (delim == ',')
            {
                openfiledialog1.Filter = "csv (*.csv)|*.csv|srf (*.srf)|*.srf|dat (*.dat)|*.dat|All Files (*.*)|*.*";
            }
            else
            {
                openfiledialog1.Filter = "All Files (*.*)|*.*|csv (*.csv)|*.csv|srf (*.srf)|*.srf|dat (*.dat)|*.dat";
            }
            openfiledialog1.FilterIndex = 1;
            openfiledialog1.Multiselect = true;
            openfiledialog1.RestoreDirectory = false;  //leave it where the files actually are for reading the raw data files (03-27-2012)

            openfiledialog1.Title = "Select file(s) to be processed:";

            openfiledialog1.ShowDialog();
            //check that one or more files were selected.
            using (new WaitCursor())
            {
                if (openfiledialog1.FileNames.Length > 0)
                {
                    string outpath = System.IO.Path.GetDirectoryName(openfiledialog1.FileName) + "\\";
                    files = openfiledialog1.FileNames;
                    srf.h1 = string_to_int(tb_h1_row.Text);
                    srf.h2 = string_to_int(tb_h2_row.Text);
                    srf.process_header(openfiledialog1.FileName, delim);
                    if (srf.line_header1 == null)
                    {
                        files = null;
                        return;
                    }
                    if (srf.h1.ToString() != tb_h1_row.Text)
                    {
                        tb_h1_row.Text = srf.h1.ToString();
                    }
                    if (srf.h2.ToString() != tb_h2_row.Text)
                    {
                        tb_h2_row.Text = srf.h2.ToString();
                    }

                    tb_fileName.Text = String.Join(Environment.NewLine, files);

                    openfiledialog1 = null;

                    header1 = srf.line_header1;
                    header2 = srf.line_header2;
                    //
                    colSet.column_def = new List<columns>();

                    if (srf.line_header1 != null)
                    {
                        for (int i = 0; i < srf.line_header1.Length; i++)
                        {
                            columns temp = new columns();
                            temp.column_num = i + 1;
                            //if (header2 != null && header2.Length > i)
                            //    temp.title = String.Format("{0} {1}", header1[i], header2[i]);
                            //else
                            //    temp.title = header1[i];
                            temp.title = header1[i];

                            temp.definition = "";
                            temp.conv_factor = 1;
                            if (ckbx_ci_pci.IsChecked == true)
                            {
                                temp.conv_factor = 1000000000000;
                            }
                            else if (ckbx_g_ug.IsChecked == true)
                            {
                                temp.conv_factor = 1000000;
                            }
                            else if (ckbx_custom.IsChecked == true)
                            {
                                temp.conv_factor = string_to_decimal(tb_custom.Text);
                            }
                            if (header1[i].ToLower() == "time")
                            {
                                temp.time = true;
                                temp.definition = "year";
                            }
                            else if (temp.title.Contains("modflow_"))
                            {
                                temp.definition = temp.title.Substring(8);
                            }
                            else
                            {
                                temp.definition = "";
                            }
                            colSet.column_def.Add(temp);
                        }
                    }
                    colSet.refresh();
                    if (tb_outdir.Text == null || tb_outdir.Text == "")
                    {
                        tb_outdir.Text = outpath + "\\";

                    }
                }
            }
        }

        private void column_settings(object sender, RoutedEventArgs e)
        {
            //winFrame.load_col_setting(colSet);
            //colSet.refresh();
            //winFrame.Show();
        }
        private void data_by_year(object sender, RoutedEventArgs e)
        {
            string message = "";
            string caption = "";
            MessageBoxButton buttons = MessageBoxButton.OK;
            using (new WaitCursor())
            {
                if (files == null || files.Length < 1)
                {
                    // Initializes the variables to pass to the MessageBox.Show method.
                    message = "No files are selected.";
                    caption = "Error Detected in Input";
                    

                    // Displays the MessageBox.
                    MessageBox.Show(message, caption, buttons);
                    return;
                }
                interpolate_data interp = new interpolate_data();
                string units = "[1/year]";
                if (ckbx_ci_pci.IsChecked == true)
                {
                    units = "[pCi/year]";
                }
                else if (ckbx_g_ug.IsChecked == true)
                {
                    units = "[ug/year]";
                }
                else if (tb_custom_unit.Text.Length > 0)
                {
                    units = "[" + tb_custom_unit.Text + "/year]";
                }

                outputs outfile = new outputs(units);

                foreach (string fileName in files)
                {
                    process_srf srf = new process_srf();
                    srf.h1 = string_to_int(tb_h1_row.Text);
                    srf.h2 = string_to_int(tb_h2_row.Text);
                    srf.process_file(fileName, delim);
                    //srf.data = srf.data;
                    bool useCum = false;
                    bool stepwise = false;
                    if (ckbx_cumulative.IsChecked == true)
                    {
                        useCum = true;
                    }
                    if (ckbx_stepwise.IsChecked == true)
                    {
                        stepwise = true;
                    }
                    interp.convert_time_yearly(srf.data, colSet.column_def, useCum, stepwise);

                    //outfile.build_ecf(interp.year_data, interp.f_data, path);
                    //outfile.build_yearly_csv_by_def(interp.year_data, path, "\t");
                    if (ckbx_Consolidate_file.IsChecked == false)
                    {
                        outfile.build_yearly_csv_by_def(interp.year_data, path, ",", fileName);
                        outfile.build_cum_csv_by_def(interp.c_data, path, fileName);
                    }
                    else
                    {
                        outfile.build_yearly_csv_single_file(interp.year_data, path, ",", fileName);
                        outfile.build_cum_csv_by_single_file(interp.c_data, path, fileName);
                    }

                }
            }
            // Initializes the variables to pass to the MessageBox.Show method.
            message = "Process Completed Successfully.";
            caption = "Process Complete";

            // Displays the MessageBox.
            MessageBox.Show(message, caption, buttons);
        }

        private void btn_outDir_Click(object sender, RoutedEventArgs e)
        {
            CommonOpenFileDialog dialog = new CommonOpenFileDialog();
            //dialog.InitialDirectory = "C:\\Users";
            dialog.IsFolderPicker = true;
            if (dialog.ShowDialog() == CommonFileDialogResult.Ok)
            {
                tb_outdir.Text = dialog.FileName;
            }
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
        }
        private int string_to_int(string s)
        {
            if (s == null || s == "")
            {
                return 0;
            }
            int x = 0;
            int.TryParse(s.Replace(" ", ""), out x);
            return x;
        }
        private decimal string_to_decimal(string s)
        {
            decimal x = 1;
            if (s == null || s == "")
            {
                return x;
            }

            try
            {
                x = decimal.Parse(s.Replace(" ", ""), System.Globalization.NumberStyles.Float);
            }
            catch
            {

            }
            
            return x;
        }
        private void check_tb_custom(object sender, TextChangedEventArgs e)
        {
            try
            {
                
                decimal x = decimal.Parse(tb_custom.Text.Replace(" ", ""), System.Globalization.NumberStyles.Float);
                e.Handled = true;
            }
            catch
            {
                e.Handled = false;
            }
            
        }
        private void set_delim(object sender, RoutedEventArgs e)
        {
            if (rb_comma.IsChecked == true)
            {
                delim = ',';
            }
            else if (rb_space.IsChecked == true)
            {
                delim = ' ';
            }
            else
            {
                delim = '\t';
            }
        }

        private void tb_outdir_TextChanged(object sender, TextChangedEventArgs e)
        {
            path = tb_outdir.Text;
        }
    }
}
