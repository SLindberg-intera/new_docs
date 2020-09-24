using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using stomp_extrap_modflow.data;
using Excel = Microsoft.Office.Interop.Excel;
using System.Windows;
using System.Runtime.InteropServices;
using System.Globalization;
using System.IO;

namespace stomp_extrap_modflow.framework
{
    class outputs
    {
        public outputs(string m)
        {
            units = m;
        }
        private string units;
        // remove any characters that would invalidate a file name and replace them with an underscore (_)
        // < (less than)
        // > (greater than)
        // : (colon - sometimes works, but is actually NTFS Alternate Data Streams)
        // " (double quote)
        // / (forward slash)
        // \ (backslash)
        // | (vertical bar or pipe)
        // ? (question mark)
        // * (asterisk)
        private string rem_invalid_char(string filename)
        {
            string new_filename = filename.Replace("<", "_").Replace(">", "_").Replace(":", "_").Replace(":", "_");
            new_filename = new_filename.Replace("\"", "_").Replace("/", "_").Replace("\\", "_").Replace("|", "_");
            new_filename = new_filename.Replace("?", "_").Replace("*", "_");
            return new_filename;
        }
        private void write_output(string fileName, string data)
        {
            //remove duplicate slashes from path
            fileName = fileName.Replace("\\\\", "\\");
            try
            {
                File.WriteAllText(fileName, data);
            }
            catch (IOException)
            {
                // Initializes the variables to pass to the MessageBox.Show method.
                string message = "Failed writing to file (" + fileName + ")!" + Environment.NewLine + Environment.NewLine + "A file with the same name may already be open by another application or user.";
                string caption = "Error Detected in Output!";
                MessageBoxButton buttons = MessageBoxButton.OK;

                // Displays the MessageBox.
                MessageBox.Show(message, caption, buttons);
                return;
            }
        }
<<<<<<< HEAD
        public void build_yearly_csv_by_def(Dictionary<string, Dictionary<decimal, decimal>> data,string path,string sep,string o_file)
=======
        public void build_yearly_csv_by_def(Dictionary<string, Dictionary<int, decimal>> data,string path,string sep,string o_file)
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
        {
            string ext = "csv";
            if(sep == "\t")
            {
                ext = "dat";
            }
            string o_filename = o_file.Substring(o_file.LastIndexOf("\\"), o_file.LastIndexOf(".") - o_file.LastIndexOf("\\"));
            foreach (string key in data.Keys.ToList())
            {
                string file_key = rem_invalid_char(key);
                string fileName = path+"\\" + o_filename + "_"+file_key +"_yearly_steps."+ext;
                string csv = key;
                csv += Environment.NewLine + "Year"+sep+ units + Environment.NewLine;
                csv += String.Join(
                    Environment.NewLine,
                    data[key].Select(d => d.Key + sep + d.Value + sep)
                );
                write_output(fileName, csv);                
            }
        }
<<<<<<< HEAD
        public void build_yearly_csv_single_file(Dictionary<string, Dictionary<decimal, decimal>> data, string path, string sep, string o_file)
=======
        public void build_yearly_csv_single_file(Dictionary<string, Dictionary<int, decimal>> data, string path, string sep, string o_file)
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
        {
            string ext = "csv";
            if (sep == "\t")
            {
                ext = "dat";
            }
            string fileName = path + "\\" + o_file.Substring(o_file.LastIndexOf("\\"),o_file.LastIndexOf(".")- o_file.LastIndexOf("\\")) + "_yearly_steps." + ext;
            string csv = o_file;
            csv += Environment.NewLine + "Time" +sep;
            csv += String.Join(sep,data.Keys.Select(d => d));
            csv += Environment.NewLine + "Year";
<<<<<<< HEAD
            Dictionary<decimal,List<decimal>> c_data = new Dictionary<decimal, List<decimal>>();
            foreach (string key in data.Keys.ToArray())
            {
                csv += sep + units;
                //int len = data[key].Keys.Count;
                foreach (Decimal year in data[key].Keys.ToArray())
=======
            Dictionary<int,List<decimal>> c_data = new Dictionary<int, List<decimal>>();
            foreach (string key in data.Keys.ToArray())
            {
                csv += sep + units;
                int len = data[key].Keys.Count;
                foreach (int year in data[key].Keys.ToArray())
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                {
                    if (!c_data.Keys.Contains(year))
                    {
                        c_data.Add(year, new List<decimal>());
                    }
                    c_data[year].Add(data[key][year]);
                }                
            }
            csv += Environment.NewLine;
            csv += String.Join(
                    Environment.NewLine,
                    c_data.Select(d => d.Key + sep + string.Join(sep, d.Value))
                );
            write_output(fileName, csv);
        }
        public void build_cum_csv_by_def(Dictionary<string, SortedDictionary<decimal, decimal>> data, string path, string o_file)
        {
            foreach (string key in data.Keys.ToList())
            {
                string o_filename = o_file.Substring(o_file.LastIndexOf("\\"), o_file.LastIndexOf(".") - o_file.LastIndexOf("\\"));
                string file_key = rem_invalid_char(key);
                string fileName = path + "\\" + o_filename + "_"+ file_key + "_cumulative.csv";
                string csv = key;
                csv += Environment.NewLine + "Year, Total " + units.Replace("/year","") + Environment.NewLine;
                csv += String.Join(
                    Environment.NewLine,
                    data[key].Select(d => d.Key + "," + d.Value + ",")
                );
                write_output(fileName, csv);
            }
        }
        public void build_cum_csv_by_single_file(Dictionary<string, SortedDictionary<decimal, decimal>> data, string path, string o_file)
        {
            string fileName = path + o_file.Substring(o_file.LastIndexOf("\\"), o_file.LastIndexOf(".") - o_file.LastIndexOf("\\")) + "_cumulative.csv";
            Dictionary<decimal, List<decimal>> c_data = new Dictionary<decimal, List<decimal>>();
            string csv = o_file;
            string sep = ",";
            csv += Environment.NewLine + "Time" + sep;
            csv += String.Join(sep, data.Keys.Select(d => d));
            foreach (string key in data.Keys.ToArray())
            {
                int len = data[key].Keys.Count;
                foreach (decimal year in data[key].Keys.ToArray())
                {
                    if (!c_data.Keys.Contains(year))
                    {
                        c_data.Add(year, new List<decimal>());
                    }
                    c_data[year].Add(data[key][year]);
                }
            }
            csv += Environment.NewLine;
            csv += String.Join(
                    Environment.NewLine,
                    c_data.Select(d => d.Key + sep + string.Join(sep, d.Value))
                );
            write_output(fileName, csv);
        }
        public void build_hss_file(string path,hssFile hss, List<cellData> files)
        {
            string output = String.Format("{0} {1} {2} {3}{4}", hss.MaxHSSSource, hss.MaxHSSCells, hss.MaxHSSStep, hss.RunOption, Environment.NewLine);
            output += string.Format("{0} {1} {2}{3}", hss.faclength, hss.factime, hss.facmass, Environment.NewLine);
            output += string.Format("{0}{1}", hss.nHSSSource, Environment.NewLine);
            foreach (cellData file in files)
            {
                output += string.Format("{0} {1}{2}",file.HSSFileName,file.inHSSFile, Environment.NewLine);
                output += string.Format("{0} {1} {2} {3} {4}{5}",file.kSource,file.iSource, file.jSource,file.SourceName,file.iHSSComp,Environment.NewLine);
            }
            write_output(path+"mt3d.hss", output);
        }
        public void build_hss_dat_files(string path,Dictionary<string, List<datafile>> data)
        {
            foreach(string file in data.Keys)
            {
                List<datafile> records = data[file];
                string output = "";
                foreach(datafile rec in records)
                {
                    output += String.Format("{0}{1}{2}{3}",rec.year.ToString("0.#####").PadRight(17,' '),rec.radius.ToString("0.#").PadRight(9,' '),rec.concentration.ToString("E9"), Environment.NewLine);
                }
                write_output(path + file, output);
            }
            
        }
        public void build_log_file(string path, List<string> log)
        {
            string fileName = path + "Log_"+ DateTime.Now.ToString("yyyyMMdd");
            string lines = String.Join(
                    Environment.NewLine,
                    log.Select(d => d)
                );
            write_output(fileName, lines);
        }

        public void build_ecf(Dictionary<string, Dictionary<int, decimal>> idata, Dictionary<string, Dictionary<decimal, decimal>> odata, string path)
        {
            //   try
            //   {
            Excel.Application excelApp = new Excel.Application();
            foreach (string key in idata.Keys)
            {
                string filename = String.Format("{0}{1}.xlsx", path,key);
                Excel.Workbook workbook = null;
                Excel.Workbooks workbooks = null;

                workbooks = excelApp.Workbooks;
                workbook = workbooks.Add(1);
                try
                {
                    

                    excelApp.Visible = false;
                    excelApp.DisplayAlerts = false;

                    Excel.Worksheet worksheet3 = (Excel.Worksheet)workbook.Sheets[1]; 
                    worksheet3.Name = "Original Data";

                    Excel.Worksheet worksheet2 = (Excel.Worksheet)workbook.Worksheets.Add();
                    worksheet2.Name = "Interpolated Data";

                    Excel.Worksheet worksheet = (Excel.Worksheet)workbook.Worksheets.Add();
                    worksheet.Name = String.Format("yearly_steps", key);

                    int i_rows = build_data_page(worksheet, key, idata[key]);
                    int o_rows = build_data_page(worksheet3, key, odata[key]);
                    build_comp_graphs(worksheet2, worksheet3, i_rows, o_rows);
                    build_orig_graphs(worksheet3, o_rows);
                    //workbook.SaveAs(filename, Microsoft.Office.Interop.Excel.XlFileFormat.xlWorkbookDefault, Type.Missing, Type.Missing,
                    //        false, false, Microsoft.Office.Interop.Excel.XlSaveAsAccessMode.xlNoChange,
                    //        Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);
                    
                }
                catch (Exception e)
                {
                    workbook.Close(false, filename, null);
                    excelApp.Quit();
                    MessageBox.Show(String.Format("Error: {0}; \n Inner Exception: {1}", e.Message, e.InnerException));
                }
                workbook.Close(true,filename,false);
                Marshal.ReleaseComObject(workbook);
                Marshal.ReleaseComObject(workbooks);

            }
            excelApp.Quit();

            Marshal.ReleaseComObject(excelApp);
            //    }
            //    catch (Exception e)
            //    {
            //        MessageBox.Show(String.Format("Error: {0}; \n Inner Exception: {1}",e.Message,e.InnerException));
            //    }
        }
        private void build_comp_graphs(Excel.Worksheet worksheet, Excel._Worksheet worksheet2, int irows, int orows)
        {
            for(int i = 1; i <= irows; i++)
            {
                string col1 = String.Format("A{0}", i);
                string col2 = String.Format("B{0}", i);
                string col3 = String.Format("C{0}", i);
                worksheet.Range[col1].Formula = String.Format("='yearly_steps'!{0}", col1);
                worksheet.Range[col2].Formula = String.Format("='yearly_steps'!{0}", col2);
                if (i == 4)
                {
                    worksheet.Range[col3].Formula = String.Format("={0}",col2);
                }
                else if (i > 4)
                {
                    worksheet.Range[col3].Formula = String.Format("=(({0} - {1}) * {2})+{3}",
                                                        col1, String.Format("A{0}", i - 1), col2, String.Format("C{0}", i - 1));
                }
            }
            Excel.ChartObjects charts = worksheet.ChartObjects();
            Excel.ChartObject chartObject = charts.Add(200, 100, 750, 400);
            Excel.Chart chart = chartObject.Chart;
            chart.ChartType = Excel.XlChartType.xlXYScatterLines;

            Excel.Series series = chartObject.Chart.SeriesCollection().Add(worksheet2.get_Range("B4", String.Format("B{0}", orows)));
            series.XValues = worksheet2.get_Range("A4", String.Format("A{0}", orows));
            series.Name = "Original Data";

            series = chartObject.Chart.SeriesCollection().Add(worksheet.Range[String.Format("B4:B{0}", irows)]);
            series.XValues = worksheet.Range[String.Format("A4:A{0}",irows)];
            series.Name = "Interpolated Data";
            series.MarkerStyle = Excel.XlMarkerStyle.xlMarkerStyleDash;
           

            chartObject = charts.Add(200, 525, 750, 400);
            chart = chartObject.Chart;
            chart.ChartType = Excel.XlChartType.xlXYScatterLines;

            series = chartObject.Chart.SeriesCollection().Add(worksheet.get_Range("B4", String.Format("B{0}", orows)));
            series.XValues = worksheet.get_Range("A4", String.Format("A{0}", orows));
            series.Name = "Original Data";

            series = chartObject.Chart.SeriesCollection().Add(worksheet.Range[String.Format("C4:C{0}", irows)]);
            series.XValues = worksheet.Range[String.Format("A4:A{0}", irows)];
            series.Name = "Interpolated Data";
            series.MarkerStyle = Excel.XlMarkerStyle.xlMarkerStyleDash;

        }
        private void build_orig_graphs(Excel.Worksheet worksheet, int orows)
        {

            Excel.ChartObjects charts = worksheet.ChartObjects();
            Excel.ChartObject chartObject = charts.Add(200, 100, 750, 400);
            Excel.Chart chart = chartObject.Chart;
            chart.ChartType = Excel.XlChartType.xlXYScatterLines;

            Excel.Series series = chartObject.Chart.SeriesCollection().Add(worksheet.get_Range("B4",String.Format("B{0}", orows)));
            series.XValues = worksheet.get_Range("A4",String.Format("A{0}", orows));
            series.Name = "Original Data";


            chartObject = charts.Add(200, 525, 750, 400);
            chart = chartObject.Chart;
            chart.ChartType = Excel.XlChartType.xlXYScatterLines;
            series = chartObject.Chart.SeriesCollection().Add(worksheet.Range[String.Format("C4:C{0}", orows)]);
            series.XValues = worksheet.Range[String.Format("A4:A{0}", orows)];
            series.Name = "Original Data";


        }
        private int build_data_page(Excel.Worksheet worksheet, string name, Dictionary<int, decimal> data)
        {
            int ind_row = 1;
            Excel.Range rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = name;
            ind_row++;
            rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = "Time";
            rng = worksheet.Range[String.Format("b{0}", ind_row)];
            rng.Value = "Flux";
            ind_row++;
            rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = "Year";
            rng = worksheet.Range[String.Format("b{0}", ind_row)];
            rng.Value = "[ci/yr]";
            foreach (int year in data.Keys.ToList())
            {
                ind_row++;
                rng = worksheet.Range[String.Format("A{0}", ind_row)];
                rng.Value = year;
                rng = worksheet.Range[String.Format("B{0}", ind_row)];
                rng.Value = data[year].ToString("E10", CultureInfo.InvariantCulture);
            }
            return ind_row;
        }
        private int build_data_page(Excel.Worksheet worksheet, string name, Dictionary<decimal, decimal> data)
        {
            int ind_row = 1;
            Excel.Range rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = name;
            ind_row++;
            rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = "Time";
            rng = worksheet.Range[String.Format("b{0}", ind_row)];
            rng.Value = "Flux";
            ind_row++;
            rng = worksheet.Range[String.Format("A{0}", ind_row)];
            rng.Value = "Year";
            rng = worksheet.Range[String.Format("b{0}", ind_row)];
            rng.Value = "[ci/yr]";
            foreach (decimal year in data.Keys.ToList())
            {
                ind_row++;
                rng = worksheet.Range[String.Format("A{0}", ind_row)];
                rng.Value = year.ToString("E", CultureInfo.InvariantCulture);
                rng = worksheet.Range[String.Format("B{0}", ind_row)];
                rng.Value = data[year].ToString("E10", CultureInfo.InvariantCulture);
            }
            return ind_row;
        }
    }
}
