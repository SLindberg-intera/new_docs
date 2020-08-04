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
        public string path_out { get; set; }
        public event PropertyChangedEventHandler PropertyChanged;
    }
}
