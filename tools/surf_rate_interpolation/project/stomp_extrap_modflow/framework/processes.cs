using System;
using System.IO;
using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using System.Threading.Tasks;
using stomp_extrap_modflow.framework;
using stomp_extrap_modflow.data;
using surf_rate_interp.data;
//using Microsoft.WindowsAPICodePack.Dialogs;
//using System.Text.RegularExpressions;
//using surf_rate_interp.framework;
using System.Xml;
using System.Windows;
<<<<<<< HEAD
using System.Text.RegularExpressions;

=======
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
namespace surf_rate_interp.framework
{
    class processes
    {
        //public Dictionary<string, Dictionary<string, Dictionary<string, string>>> proc_files;
        public List<configCols> proc_files = new List<configCols>();
        public void process_config(string config)
        {  
            string units = "1/year";
            string dir = "--";
            string fileName = "--";
            string conv_factor = "1";
            string first_header = "1";
            string last_header = "1";
            string delim = ",";
            string use_cumulative = "true";
            string consolidate_file = "true";
            string path_out = "";
<<<<<<< HEAD
            string step_wise = "false";
            Dictionary<int, string> cols = new Dictionary<int, string>();
=======
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
            //string cols;
            

            using (XmlReader reader = XmlReader.Create(@config))
            {
                while (reader.Read())
                {
                    string node = reader.Name.ToString().ToLower();

                    switch (node)
                    {
                        case "dir":
                            //
                            dir = reader.GetAttribute("name");
                            break;
                        case "file":
                            //file will be found twice, the beginning of the element (<file name="XXXX">)
                            //in which case it will have a value for attribute 'name' and the end of the 
                            //element (<\file>) in which case it wont have a 'name' attribute
                            string t_fileName = reader.GetAttribute("name");
                            if(t_fileName == null)
                            {
                                //process_file(units, dir, fileName, conv_factor, first_header, last_header, delim, use_cumulative, 
                                //             consolidate_file, path_out);
                                List<string> files = new List<string>();
                                if (fileName.ToLower() == "all")
                                {
                                    foreach (string file in Directory.GetFiles(dir))
                                    {
                                        files.Add(file);
                                    }
<<<<<<< HEAD
                                    
=======
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                                }
                                else
                                {
                                    string fullPath = Path.Combine(dir, fileName);
                                    files.Add(fullPath);
                                }
                                foreach (string file in files)
                                {
                                    configCols temp = new configCols();
                                    temp.dir = dir;
                                    temp.file = file;
                                    temp.units = units;
                                    temp.conv_factor = Convert.ToDecimal( conv_factor);
                                    temp.first_header = Convert.ToInt32(first_header);
                                    temp.last_header = Convert.ToInt32(last_header);
                                    temp.delim = Convert.ToChar(delim);
                                    temp.use_cumulative = Convert.ToBoolean(use_cumulative);
                                    temp.consolidate_file = Convert.ToBoolean(consolidate_file);
<<<<<<< HEAD
                                    temp.step_wise = Convert.ToBoolean(step_wise);
                                    temp.path_out = path_out;
                                    temp.columns = cols;

                                    cols = new Dictionary<int, string>();
                                    proc_files.Add(temp);
                                    
                                }
                                units = "";
                                conv_factor = "";
                                first_header = "";
                                last_header = "";
                                delim = "";
                                use_cumulative = "";
                                consolidate_file = "";
                                step_wise = "false";
                                path_out = "";

=======
                                    temp.path_out = path_out;
                                    proc_files.Add(temp);
                                }
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                            }
                            else
                            {
                                fileName = t_fileName;
                            }
                            break;
                        case "units":
                            units = reader.ReadString();
                            Console.WriteLine("Units: " + reader.ReadString());
                            break;
                        case "conv_factor":
                            decimal cf = 0;
                            conv_factor = reader.ReadString();
                            if (!Decimal.TryParse(conv_factor, out cf))
                            {
                                MessageBox.Show("Error: \nInvalid conv_factor ("+ reader.ReadString() + ") for file" + fileName);
                                Environment.Exit(1);
                            }
                            
                            break;
                        case "first_header":
                            first_header = reader.ReadString();
                            break;
                        case "last_header":
                            last_header = reader.ReadString();
                            break;
                        case "delim":
                            delim = reader.ReadString();
                            break;
                        case "use_cumulative":
                            use_cumulative = reader.ReadString();
                            break;
                        case "consolidate_file":
                            consolidate_file = reader.ReadString();
                            break;
                        case "path_out":
                            path_out = reader.ReadString();
                            break;
<<<<<<< HEAD
                        case "step_wise":
                            step_wise = reader.ReadString();
                            break;
                        case "col":
                            string t_col = reader.GetAttribute("index");
                            int index = -1;
                            if (t_col != null && int.TryParse(t_col, out index))
                            {
                                cols[index] = reader.ReadString();
                            }
                            break;
=======
                        //case "cols":
                        //    cols = reader.ReadString();
                        //    break;
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                    }
                }
                //process_file(units, dir, fileName, conv_factor, first_header,last_header, delim, use_cumulative,consolidate_file,path_out);
            }
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
<<<<<<< HEAD
        private List<columns> build_custom_cols(Dictionary<int,string> custom, decimal conv_factor)
        {
            List<columns> cols = new List<columns>();
            foreach (int key in custom.Keys)
            {
                columns temp = new columns();
                temp.column_num = key+1;
                temp.title = custom[key];

                temp.definition = "";
                temp.conv_factor = conv_factor;

                if (custom[key].ToLower() == "time" || custom[key].ToLower() == "year")
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
                    temp.definition = custom[key];
                }
                cols.Add(temp);
            }
            return cols;
        }
        private List<columns> build_orig_cols(string[] header1,decimal conv_factor)
        {
            //format of columns '##-##'
            var r = new Regex("^\\d*-\\d*$");
            
            List<columns> cols = new List<columns>();
            for (int i = 0; i < header1.Length; i++)
=======
        public void process_file(configCols rec)//string units, string dir, string file, decimal conv_factor, 
                                  //int first_header, int last_header, char delim, bool use_cumulative,
                                  //bool consolidate_file, string path_out)
        {
            //List<string> files = new List<string>();
            //MessageBox.Show("data: \n" + fileName);
            //if (fileName.ToLower() == "all")
            //{
            //    foreach (string file in Directory.GetFiles(dir))
            //    {
            //        files.Add(file);
            //    }
            //}
            //else
            //{
            //    string fullPath = Path.Combine(dir,fileName);
            //    files.Add(fullPath);
            //}
            //MessageBox.Show("File: \n\n" + files[0]);
            //foreach (string file in files)
            //{
            process_srf srf = new process_srf();
            srf.h1 = rec.first_header;
            srf.h2 = rec.last_header;
            srf.process_header(rec.file, rec.delim);
            List<columns> cols = new List<columns>();
            for (int i = 0; i < srf.line_header1.Length; i++)
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
            {
                columns temp = new columns();
                temp.column_num = i + 1;
                //if (header2 != null && header2.Length > i)
                //    temp.title = String.Format("{0} {1}", header1[i], header2[i]);
                //else
                //    temp.title = header1[i];
<<<<<<< HEAD
                temp.title = header1[i];

                temp.definition = "";
                temp.conv_factor = conv_factor;

                if (header1[i].ToLower() == "time")
=======
                temp.title = srf.line_header1[i];

                temp.definition = "";
                temp.conv_factor = rec.conv_factor;

                if (srf.line_header1[i].ToLower() == "time")
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                {
                    temp.time = true;
                    temp.definition = "year";
                }
                else if (temp.title.Contains("modflow_"))
                {
                    temp.definition = temp.title.Substring(8);
                }
<<<<<<< HEAD
                else if (r.IsMatch(temp.title))
                {
                    temp.definition = temp.title;
                }
=======
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
                else
                {
                    temp.definition = "";
                }
                cols.Add(temp);
            }
<<<<<<< HEAD
            return cols;
        }
        //build  columns and initiate interpolation process for a give file.
        public void process_file(configCols rec)//string units, string dir, string file, decimal conv_factor, 
                                  //int first_header, int last_header, char delim, bool use_cumulative,
                                  //bool consolidate_file, string path_out)
        {
            //MessageBox.Show("data: \n" + fileName);
            process_srf srf = new process_srf();
            srf.h1 = rec.first_header;
            srf.h2 = rec.last_header;
            srf.process_header(rec.file, rec.delim);
            List<columns> cols = new List<columns>();
            if (rec.columns.Count > 0)
            {
                //MessageBox.Show("data: using custom column names");
                cols = build_custom_cols(rec.columns, rec.conv_factor);
            }
            else
            {
                //MessageBox.Show("data: using file defined column names");
                cols = build_orig_cols(srf.line_header1, rec.conv_factor);
            }

=======
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
            interpolate_data interp = new interpolate_data();

            outputs outfile = new outputs(rec.units);

            srf.process_file(rec.file, rec.delim);

<<<<<<< HEAD
            interp.convert_time_yearly(srf.data, cols, rec.use_cumulative, rec.step_wise);
=======
            interp.convert_time_yearly(srf.data, cols, rec.use_cumulative);
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964

            if (rec.consolidate_file == false)
            {
                outfile.build_yearly_csv_by_def(interp.year_data, rec.path_out, ",", rec.file);
                outfile.build_cum_csv_by_def(interp.c_data, rec.path_out, rec.file);
            }
            else
            {
                outfile.build_yearly_csv_single_file(interp.year_data, rec.path_out, ",", rec.file);
                outfile.build_cum_csv_by_single_file(interp.c_data, rec.path_out, rec.file);
            }
<<<<<<< HEAD
        }
=======
            //}
        }
        
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
    }
}
