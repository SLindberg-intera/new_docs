using System;
using System.Collections.Generic;
using System.Globalization;
//using System.Data;
using System.IO;
//using System.Linq;
//using System.Text;
//using System.Threading.Tasks;
using System.Text.RegularExpressions;
using System.Windows;


namespace stomp_extrap_modflow.framework
{
    
    class process_srf
    {
        private static readonly Regex _regex = new Regex(@"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$");
        public Dictionary<int, decimal[]> data = new Dictionary<int, decimal[]>();
        public string[] line_header1;
        public string[] line_header2;
        public int h1 = 0;
        public int h2 = 0;

        public void process_header(string fileName,char delim)
        {
            IEnumerable<string> lines = new List<string>();
            try
            {
                lines = File.ReadLines(fileName);
            }
            catch (IOException)
            {
                // Initializes the variables to pass to the MessageBox.Show method.
                string message = "Cannot open file ("+fileName+")."+ Environment.NewLine + Environment.NewLine + "The file may already be open by another application or user.";
                string caption = "Error Detected in Input";
                MessageBoxButton buttons = MessageBoxButton.OK;

                // Displays the MessageBox.
                MessageBox.Show(message, caption, buttons);
                line_header1 = null;
                line_header2 = null;
                return;
            }
            int i = 1;
            bool h1_set = false;
            bool h2_set = false;
            if (h1 > 0)
                h1_set = true;
            if (h2 > 0)
                h2_set = true;
            string[] last_line1 = new string[1];
            string[] last_line2 = new string[1];
            line_header1 = null;
            line_header2 = null;
            foreach(string line in lines)
            {
                string temp = remove_extra_spaces(line.Trim(' '));
                if (h1_set && line_header1 == null)
                {
                    if (i == h1)
                    {
                        last_line1 = temp.Split(new[] { delim }, StringSplitOptions.None);
                    }

                }
                //else if (h1 == 0 && line.Length > 5)
                //{


                //    //if (line.Trim(' ').Substring(0, 5).ToLower() == "time " || line.Trim(' ').Substring(0, 5).ToLower() == "year ")
                //    //{
                //    //string temp = remove_extra_spaces(line.Trim(' '));
                //    line_header1 = temp.Split(new[] { delim }, StringSplitOptions.None);
                //    h1 = i;
                //    h2 = i + 1;
                //    //}
                //}
                else if (h2_set)
                {
                    if (i == h2)
                    {
                        last_line2 = temp.Split(new[] { delim }, StringSplitOptions.None);
                        break;
                    }
                }
                ////else if (h1 > 0 && h2 == 0 && line.Length > 5)
                //else if (h2 == i)
                //{

                //    if (line.Trim(' ').Substring(0,1) == "[")
                //    {
                //        line_header2 = temp.Split(new[] { delim }, StringSplitOptions.None);
                //        h2 = i;
                //    }
                //}
                else
                {
                    // if the line has data then we have passed the headers
                    if (_regex.IsMatch(temp.Split(new[] { delim }, StringSplitOptions.None)[0]) && _regex.IsMatch(temp.Split(new[] { delim }, StringSplitOptions.None)[1]))
                    {
                        
                        break;
                    }
                    //check if there is a first line yet. if not set it
                    else if (last_line1.Length < 2)
                    {
                        last_line1 = temp.Split(new[] { delim }, StringSplitOptions.None);
                        h1 = i;
                    }
                    //if first line exists check if the second line has be set.
                    else if (last_line2.Length < 2)
                    {
                        last_line2 = temp.Split(new[] { delim }, StringSplitOptions.None);
                        h2 = i;
                    }
                    
                    //As the new line is not data, move line2 to line1 and set line2 as the current line.
                    else
                    {
                        if (last_line1[0].ToLower() != "time")
                        {
                            last_line1 = last_line2;
                            h1 = i - 1;
                        }
                        last_line2 = temp.Split(new[] { delim }, StringSplitOptions.None);
                        h2 = i;
                    }
                }
                i++;
            }
            if (last_line1.Length < 2 )
            {
                line_header1 = new string[0];
            }
            else
            {
                line_header1 = last_line1;
            }
            if (last_line2.Length < 2)
            {
                line_header2 = new string[0];
            }
            else
            {
                line_header2 = last_line2;
            }

        }

        public void process_file(string fileName,  char delim)
        {
            //bool header1 = false;
            //bool header2 = false;
            bool firstline = false;          
            
            int i = 0;
            int row = 0;
            int line_num = 0;
            //DataTable data = new DataTable();
            IEnumerable<string> lines = File.ReadLines(fileName);
            foreach (var x in lines)
            {
                line_num++;
                string line = remove_extra_spaces(x.Trim(' '));
                if (line.Length > 3)
                {
                    string[] parsed;
                    if (line_num > h1 && line_num > h2)
                    {

                        //if (firstline == false)
                        //{
                        //    //looking for numeric
                        //    if (int.TryParse(line.Substring(0, 1), out i))
                        //    {
                        //        firstline = true;
                        //        parsed = line.Split(new[] { delim }, StringSplitOptions.None);

                        //        row++;
                        //        data.Add(row, Array.ConvertAll<string, decimal>(parsed, decimal.Parse));
                        //    }

                        //}
                        //else //header 1 = true and header 2 = true
                        //{
                            if (int.TryParse(line.Substring(0, 1), out i))
                            {
                                parsed = line.Split(new[] { delim }, StringSplitOptions.None);
                                row++;
                                data.Add(row, new decimal[parsed.Length]);
                                for(int ind = 0; ind < parsed.Length; ind++)
                                {
                                    if(parsed[ind].Length > 0)
                                        data[row][ind] = decimal.Parse(parsed[ind], NumberStyles.AllowExponent | NumberStyles.AllowDecimalPoint | NumberStyles.AllowLeadingSign);
                                }
                                //data.Add(row, Array.ConvertAll<string, decimal>(parsed, decimal.Parse));
                            }
                        //}
                    }
                }
            }
            i = 0;
        }
        private string remove_extra_spaces(string line)
        {
            string temp = line;
            //Remove extra white spaces for easier parsing
            int i = 0;
            while (temp.Length != i)
            {
                i = temp.Length;
                temp = temp.Replace("  ", " ").Replace(" ]", "]").Replace("( ", "(");
            }
            return temp;
        }
    }
}
