using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using stomp_extrap_modflow.data;
using System.IO;
using System.Windows;

namespace stomp_extrap_modflow.framework
{
    class hssp_threaded
    {
    //    private List<string> log;
    //    private List<hss_data_files> source = new List<hss_data_files>();
    //    private Dictionary<string, List<datafile>> data = new Dictionary<string, List<datafile>>();
    //    static object _ActiveWorkersLock = new object();
    //    static int _CountOfActiveWorkers = 0;

    //    public hssp_threaded(List<hss_data_files> s)
    //    {
    //        source = s;
            
    //    }
    //    public void build_hssp(char delim, int start, int end, string path)
    //    {
    //        ThreadPool.SetMinThreads(1, 0);
    //        ThreadPool.SetMaxThreads(2, 0);
    //        List<cellData> files = new List<cellData>();
    //        string[] sourceFiles = source.Select(s => s.source).Distinct().ToArray();
    //        foreach(string sourceFile in sourceFiles)
    //        {

    //            List<hss_data_files> sub_source = source.Where(s => s.source == sourceFile).ToList();
    //            IEnumerable<string> lines = File.ReadLines(sourceFile);
    //            foreach(hss_data_files file in sub_source)
    //            {
    //                int col_year = sub_source.Where(s => s.time == true).Select(s => s.col).First();
    //                if (file.i != null && file.i != "" && file.j != null && file.j != "")
    //                {
    //                    string datFileName = String.Format("i{0}j{1}_HSS.dat", file.i, file.j);
    //                    cellData cell = files.Where(f => f.HSSFileName == file.source).FirstOrDefault();
    //                    if (cell == null || cell.HSSFileName == null)
    //                    {
                            
    //                        cell = new cellData();
    //                        cell.HSSFileName = datFileName;
    //                        cell.iHSSComp = "COPC";
    //                        cell.inHSSFile = file.id.ToString();
    //                        cell.iSource = file.i.ToString();
    //                        cell.jSource = file.j.ToString();
    //                        cell.kSource = file.k.ToString();
    //                        cell.SourceName = file.id.ToString();
    //                        files.Add(cell);
    //                    }
    //                    if (!data.ContainsKey(datFileName))
    //                    {
    //                        data.Add(datFileName, new List<datafile>());
    //                    }
    //                    hssp_thread build1 = new hssp_thread(cell, lines, file, delim, col_year, start, end, ref data);
    //                    lock (_ActiveWorkersLock)
    //                        ++_CountOfActiveWorkers;
    //                    ThreadPool.QueueUserWorkItem(new WaitCallback(Process), build1);
    //                }
    //                //wait for file to finish processing.  IMPORTANT!!
    //                //Some Source files may have additional information for a cell
    //                // to avoid overwriting process one file at a time.
    //                lock (_ActiveWorkersLock)
    //                {
    //                    while (_CountOfActiveWorkers > 0)
    //                        Monitor.Wait(_ActiveWorkersLock);
    //                }
    //            }
    //        }
            
    //    }

    //    static void Process(Object obj)
    //    {
    //        hssp_thread build = obj as hssp_thread;
    //        try
    //        {
    //            build.build_data_file();
                
    //        }
    //        catch (Exception e)
    //        {
    //            string tmp = String.Format("***Error while building {0}.  Error: {1}", build.cell.HSSFileName, e.Message.ToString());
    //            MessageBox.Show(tmp);
    //        }
    //        finally
    //        {
    //            lock (_ActiveWorkersLock)
    //            {
    //                --_CountOfActiveWorkers;
    //                Monitor.PulseAll(_ActiveWorkersLock);
    //            }
    //        }

    //    }
    //}
    //class hssp_thread
    //{
    //    public string fileName;
    //    private Dictionary<string, List<datafile>> data;
    //    public List<string> log;
    //    public cellData cell;
    //    private IEnumerable<string> lines;
    //    private hss_data_files file;
    //    private char delim;
    //    private int col_year;
    //    private int start;
    //    private int end;
    //    public hssp_thread(cellData c, IEnumerable<string> l, hss_data_files f, char d, int cy, int s, int e, ref Dictionary<string, List<datafile>> dat)
    //    {
    //        cell = c;
    //        lines = l;
    //        file = f;
    //        delim = d;
    //        col_year = cy;
    //        start = s;
    //        end = e;
    //        data = dat;
    //        log = new List<string>();
    //        fileName = String.Format("{0} ({1}-{2}", f.source, f.i,f.j);
    //    }
    //    [STAThread]
    //    public void build_data_file()
    //    {
    //        log.Add(string.Format("{0}:  processing file '{1}'; column {2}; cell {3}-{4}; time frame {5} - {6} ",
    //                            DateTime.Now, file.source, file.col, file.i, file.j, start, end));
            
    //        //data.Add(cell.HSSFileName, new List<datafile>());
    //        bool start_year = true;
    //        string log_str = "";
    //        double days = 0;
    //        double prev_year = start;
    //        foreach (string line in lines)
    //        {
    //            string[] temp = line.Split(new[] { delim }, StringSplitOptions.None);
    //            double year = 0;

    //            if (double.TryParse(temp[col_year], out year))
    //            {

    //                if (year >= start && year <= end)
    //                {
    //                    double x = 0;

    //                    if (double.TryParse(temp[file.col], out x))
    //                    {
    //                        //if the first record is > than the start date, then backfill previous years.
    //                        if (start_year)
    //                        {
    //                            if (year > start)
    //                            {
    //                                log.Add(string.Format("{0}:  Backfilling missing years ({1} - {2}",
    //                                        DateTime.Now, start, year - 1));
    //                                for (int i = start; i < year; i++)
    //                                {
    //                                    if (i > start)
    //                                    {

    //                                        log_str = string.Format("{0}:  year calc: (({1} - {2}) * 365.25) + {3} = ",
    //                                                DateTime.Now, i, i - 1, days);
    //                                        days += year_to_days(i - 1, i);
    //                                        log.Add(log_str + days.ToString());
    //                                    }

    //                                    datafile rec = data.FirstOrDefault(d => d.year == days);
    //                                    data.Add(datafile_rec(days, x, data.FirstOrDefault(d => d.year == days)));
    //                                    prev_year = i;
    //                                }
    //                                log.Add(string.Format("{0}:  End of backfilled years",
    //                                        DateTime.Now, start, year - 1));
    //                            }
    //                            start_year = false;
    //                        }
    //                        if (year > start)
    //                        {
    //                            log_str = string.Format("{0}:  year calc: (({1} - {2}) * 365.25) + {3} = ",
    //                                                DateTime.Now, year, prev_year, days);
    //                            days += year_to_days(prev_year, year);
    //                            log.Add(log_str + days.ToString());
    //                        }
    //                        data.Add(datafile_rec(days, x, data.FirstOrDefault(d => d.year == days)));
    //                        prev_year = year;
    //                    }
    //                }
    //            }
    //        }
    //    }
    //    private double year_to_days(double start, double end)
    //    {
    //        return (end - start) * 365.25;
    //    }
    //    private datafile datafile_rec(double days, double x, datafile rec)
    //    {
    //        if (rec == null || rec.year < 1)
    //        {
    //            rec = new datafile();
    //            rec.year = days;
    //            rec.radius = 0.0;
    //            rec.concentration = x;
    //            log.Add(string.Format("{0}: year = {1}; Radius = {2}; concentration (0 + {3}) = {4}",
    //                DateTime.Now, rec.year, rec.radius, rec.concentration, rec.concentration));
    //        }
    //        else
    //        {
    //            log.Add(string.Format("{0}: year = {1}; Radius = {2}; concentration ({3} + {4}) = {5}",
    //                DateTime.Now, rec.year, rec.radius, rec.concentration, x, rec.concentration + x));
    //            rec.concentration += x;
    //        }

    //        return rec;
    //    }
    }
}

//foreach (string sourceFile in sourceFiles)
//{

//    
//}