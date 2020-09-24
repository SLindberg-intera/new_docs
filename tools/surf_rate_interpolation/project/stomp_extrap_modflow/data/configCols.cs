using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using System.ComponentModel;
namespace surf_rate_interp.data
{
    class configCols : INotifyPropertyChanged
    {
        public string dir { get; set; }
        public string file { get; set; }
        public bool processed { get; set; }
        public string units { get; set; }
        public decimal conv_factor { get; set; }
        public int first_header { get; set; }
        public int last_header { get; set; }
        public char delim { get; set; }
        public bool use_cumulative { get; set; }
        public bool consolidate_file { get; set; }
<<<<<<< HEAD
        public bool step_wise { get; set; }
        public string path_out { get; set; }
        public Dictionary<int,string> columns { get; set; }
=======
        public string path_out { get; set; }
>>>>>>> 34796230d42aba5da76e46f7c6e4fd1080c3a964
        public event PropertyChangedEventHandler PropertyChanged;
    }
}
