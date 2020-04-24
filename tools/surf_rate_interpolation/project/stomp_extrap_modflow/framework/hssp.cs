using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using stomp_extrap_modflow.data;
using System.IO;
using System.Text.RegularExpressions;
using System.Windows;
using System.Runtime.Serialization.Formatters.Binary;

namespace stomp_extrap_modflow.framework
{
    class hssp
    {
        private List<string> log;
        public List<hss_data_files> source = new List<hss_data_files>();
        private static readonly Regex _regex = new Regex("[^0-9]+"); //regex that matches disallowed text
        //private static readonly Regex _regex2 = new Regex("[^0-9]+"); //regex that matches disallowed text
        private Dictionary<int, Dictionary<int, int>> water_lvl;
        public void build_package_references(string fileName)
        {
            water_lvl = new Dictionary<int, Dictionary<int, int>>();
            IEnumerable<string> lines = File.ReadLines(fileName);
            foreach(string line in lines)
            {
                string[] temp = line.Split(',');
                int i = 0;
                int j = 0;
                int k = 0;
                if(int.TryParse(temp[0], out i) && int.TryParse(temp[1], out j) && int.TryParse(temp[2], out k))
                {
                    //currently starts at 0, so each val needs to be increased by 1.
                    i++;
                    j++;
                    k++;
                    if(!water_lvl.Keys.Contains(i))
                    {
                        water_lvl.Add(i, new Dictionary<int, int>());
                    }
                    if(!water_lvl[i].Keys.Contains(j))
                    {
                        water_lvl[i].Add(j, k);
                    }
                    else if(water_lvl[i][j] < k)
                    {
                        water_lvl[i][j] = k;
                    }
                }
            }
            //foreach (string l in lines)
            //{
            //})


            //--------
            //string[] files = Directory.GetFiles(dir, "*.spc");
            //string line = File.ReadLines(files[0]).FirstOrDefault();
            //int max_i = 0;
            //int max_j = 0;
            //int.TryParse(line.Substring(0, line.IndexOf(" ")).Trim(' '), out max_i);
            //int.TryParse(line.Substring(line.IndexOf(" ")).Trim(' '), out max_j);

            //files = Directory.GetFiles(dir, "*.hds");
            //IEnumerable<string> lines = File.ReadAllBytes(files[0]);
            //lines = File.ReadLines(files[0]);
            //foreach (string l in lines)
            //{
            //}

            //files = files = Directory.GetFiles(dir, "top*.ref");
            //IEnumerable<string> lines =File.ReadLines(dir + "P2Rv8.2.hds");
            //foreach (string l in lines)
            //{
            //}

            //files = files = Directory.GetFiles(dir, "bottom*.ref");
            //foreach (string f in files)
            //{
            //    lines = File.ReadLines(f);
            //    foreach (string l in lines)
            //    {
            //    }
            //}
        }
        public void build_source_data(string fileName, bool consolidated)
        {
            hss_data_files temp = new hss_data_files();
            if (consolidated)
            {
                IEnumerable<string> lines = File.ReadLines(fileName);
                string[] line = lines.First().Split(new[] { '\t' }, StringSplitOptions.None);
                int x = 0;
                foreach(string col in line)
                {
                    temp = new hss_data_files();
                    temp.col = x;
                    temp.source = fileName;
                    temp.name = String.Format("{0} ({1})", fileName,col);
                    string[] loc = new string[2];
                    if (col.Contains("_"))
                    {
                        loc = col.Split(new[] { '_' }, StringSplitOptions.None);
                    }
                    else if (col.Contains(","))
                    {
                        loc = col.Split(new[] { ',' }, StringSplitOptions.None);
                    }
                    else if (col.Contains("-"))
                    {
                        loc = col.Split(new[] { '-' }, StringSplitOptions.None);
                    }
                    else if (col.ToLower() == "year" || col.ToLower()=="yr")
                    {
                        temp.time = true;
                    }
                    if (loc[0] != null && loc[1] != null)
                    {
                        bool match = !_regex.IsMatch(loc[0]);
                        if (loc[0].Length > 0 && match)
                        {
                            match = !_regex.IsMatch(loc[1]);
                            if (loc[1].Length > 0 && match)
                            {
                                temp.i = loc[0];
                                temp.j = loc[1];
                            }
                        }
                    }
                    if (source.Count > 0)
                        temp.id = source.Count + 1;
                    source.Add(temp);
                    x++;
                }
            }
            else
            {
                if (source.Count > 0)
                    temp.id = source.Count + 1;
                temp.source = fileName;

            }
        }
        public void buildHSS(char delim, int start, int end, string path)
        {
            List<cellData> files = new List<cellData>();
            Dictionary<string, List<datafile>> data = new Dictionary<string, List<datafile>>();
            hssFile hss = new hssFile();
            log = new List<string>();
            string log_str = "";
            
            foreach (hss_data_files file in source)
            {
                
                if (file.i != null && file.i != "" && file.j != null && file.j != "")
                {
                    string datFileName = String.Format("i{0}j{1}_HSS.dat", file.i, file.j);
                    cellData cell = files.Where(f => f.HSSFileName == file.source).FirstOrDefault();
                    if (cell == null || cell.HSSFileName == null)
                    {
                        log.Add(string.Format("{0}:  processing file '{1}'; column {2}; cell {3}-{4}; time frame {5} - {6} ", 
                            DateTime.Now, file.source,file.col,file.i,file.j,start, end));
                        cell = new cellData();
                        cell.HSSFileName = datFileName;
                        cell.iHSSComp = "COPC";
                        cell.inHSSFile = "";//file.id.ToString();
                        cell.iSource = file.i.ToString();
                        cell.jSource = file.j.ToString();
                        if (water_lvl.Keys.Contains(int.Parse(file.i)) && water_lvl[int.Parse(file.i)].Keys.Contains(int.Parse(file.j)))
                        {
                            cell.kSource = water_lvl[int.Parse(file.i)][int.Parse(file.j)].ToString();
                        }
                        else
                        {
                            cell.kSource = file.k.ToString();
                        }
                        cell.SourceName = file.id.ToString();
                        files.Add(cell);
                    }
                    int col_year = source.Where(s => s.source == file.source && s.time == true).Select(s => s.col).First();
                    IEnumerable<string> lines = File.ReadLines(file.source);
                    double prev_year = start;
                    double days = 0;
                    bool start_year = true;
                    
                    foreach (string line in lines)
                    {
                        string[] temp = line.Split(new[] { delim }, StringSplitOptions.None);
                        double year = 0;
                        
                        if (!data.ContainsKey(datFileName))
                        {
                            data.Add(datFileName, new List<datafile>());
                        }

                        if (double.TryParse(temp[col_year], out year))
                        {
                            
                            if (year >= start && year <= end)
                            {
                                double x = 0;
                                                                
                                if (double.TryParse(temp[file.col], out x))
                                {
                                    if(x > 0)
                                    {
                                        x = x / 365.25;
                                    }
                                    //if the first record is > than the start date, then backfill previous years.
                                    if (start_year)
                                    {
                                        if (year > start)
                                        {
                                            log.Add(string.Format("{0}:  Backfilling missing years ({1} - {2}",
                                                    DateTime.Now, start, year-1));
                                            for (int i = start; i < year; i++)
                                            {
                                                if (i > start)
                                                {
                                                    
                                                    log_str = string.Format("{0}:  year calc: (({1} - {2}) * 365.25) + {3} = ",
                                                            DateTime.Now, i, i-1, days);
                                                    days += year_to_days(i - 1, i);
                                                    log.Add(log_str + days.ToString());
                                                }
                                                
                                                datafile rec = data[datFileName].FirstOrDefault(d => d.year == days);
                                                data[datFileName].Add(datafile_rec(days, 0, data[datFileName].FirstOrDefault(d => d.year == days)));
                                                if(days > 0)
                                                {
                                                    data[datFileName].Add(datafile_rec(days, 0, data[datFileName].FirstOrDefault(d => d.year == days)));
                                                }
                                                prev_year = i;
                                            }
                                            log.Add(string.Format("{0}:  End of backfilled years",
                                                    DateTime.Now, start, year - 1));
                                        }
                                        start_year = false;
                                    }
                                    if (year > start)
                                    {
                                        log_str = string.Format("{0}:  year calc: (({1} - {2}) * 365.25) + {3} = ",
                                                            DateTime.Now, year, prev_year, days);
                                        days += year_to_days(prev_year, year);
                                        log.Add(log_str + days.ToString());
                                    }
                                    data[datFileName].Add(datafile_rec(days, x, data[datFileName].FirstOrDefault(d => d.year == days)));
                                    if(days > 0)
                                    {
                                        data[datFileName].Add(datafile_rec(days, x, data[datFileName].FirstOrDefault(d => d.year == days)));
                                    }
                                    prev_year = year;
                                }                                
                            }
                        }
                    }
                }
            }
            hss.MaxHSSSource = files.Count;
            hss.MaxHSSCells = files.Count;
            hss.nHSSSource = files.Count;
            hss.MaxHSSStep = (end - start) + 2;
            string units = "";
            outputs output = new outputs(units);
            output.build_hss_file(path, hss, files);
            output.build_hss_dat_files(path, data);
            output.build_log_file(path, log);
            log = new List<string>();
        }
        private double year_to_days(double start, double end)
        {
            return (end - start) * 365.25;
        }
        private datafile datafile_rec(double days, double x, datafile rec)
        {
            if (rec == null || rec.year < 1)
            {
                rec = new datafile();
                rec.year = days;
                rec.radius = 0.0;
                rec.concentration = x;
                log.Add(string.Format("{0}: year = {1}; Radius = {2}; concentration (0 + {3}) = {4}",
                    DateTime.Now, rec.year, rec.radius, rec.concentration, rec.concentration));
            }
            else
            {
                log.Add(string.Format("{0}: year = {1}; Radius = {2}; concentration ({3} + {4}) = {5}",
                    DateTime.Now, rec.year, rec.radius, rec.concentration, x, rec.concentration + x));
                rec.concentration += x;
            }
            
            return rec;
        }
    }
}
