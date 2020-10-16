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
//using stomp_extrap_modflow.gui;
using surf_rate_interp.data;
using Microsoft.WindowsAPICodePack.Dialogs;
using System.Text.RegularExpressions;
using surf_rate_interp.framework;
using surf_rate_interp.gui;
using System.ComponentModel;
namespace surf_rate_interp.gui
{
    /// <summary>
    /// Interaction logic for Interpolate.xaml
    /// </summary>
    public partial class config_interp : Page
    {
        BackgroundWorker MyWorker = new System.ComponentModel.BackgroundWorker();
        private columnConfig colSet = new columnConfig();
        private Cursor _previousCursor;

        public config_interp(string config)
        {
            InitializeComponent();
            winFrame.Content = colSet;
            colSet.column_def = new List<configCols>();
            lbl_config.Text = config;
            //set up background process for processing
            MyWorker.DoWork += MyWorker_DoWork;
            MyWorker.RunWorkerCompleted += MyWorker_RunWorkerCompleted;
            _previousCursor = Mouse.OverrideCursor;
            Mouse.OverrideCursor = Cursors.Wait;
            MyWorker.RunWorkerAsync(config);
        }
        //Delegate that background process uses to update UI
        private delegate void DelegateUpdateLabel(int i);
        private void UpdateLabel(int i)
        {
            lbl_progress.Content = "files left:" + i.ToString();
        }
        private delegate void DelegateUpdateFileList(configCols rec);
        private void UpdateFileList(configCols rec)
        {
            colSet.column_def.Add(rec);
            colSet.refresh();
        }
        private delegate void DelegateUpdateUpdateProgressBar(double i);
        private void UpdateProgressBar(double i)
        {
            ProgressBar.Value = i;
        }
        
        //Background processes
        //process files from Config.xml
        private void MyWorker_DoWork(object Sender, System.ComponentModel.DoWorkEventArgs e)
        {
            DelegateUpdateLabel Upd_Del_label = new DelegateUpdateLabel(UpdateLabel);
            DelegateUpdateFileList Upd_file_list = new DelegateUpdateFileList(UpdateFileList);
            DelegateUpdateUpdateProgressBar upd_prog_bar = new DelegateUpdateUpdateProgressBar(UpdateProgressBar);
            processes proc_config = new processes();
            proc_config.process_config(e.Argument.ToString());
            int file_count = proc_config.proc_files.Count;
            label1.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, Upd_Del_label, file_count);
            ProgressBar.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, upd_prog_bar, 0);
            for (int i = 0; i < file_count; i++)
            {
                proc_config.process_file(proc_config.proc_files[i]);
                proc_config.proc_files[i].processed = true;
                double perc = (Convert.ToDouble(i + 1) / Convert.ToDouble(file_count)) * 100;
                lbl_progress.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, Upd_Del_label, file_count - (i + 1));
                ProgressBar.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, upd_prog_bar, perc);
                

                colSet.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, Upd_file_list, proc_config.proc_files[(i)]);
            }
            e.Cancel = false;
            return;

        }
        //after background process finishes.
        private void MyWorker_RunWorkerCompleted(object Sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            if (e.Cancelled)
            {
                lbl_progress.Content = "Error: process may have been canceled.";
            }
            else
            {
                lbl_progress.Content = "All files processed";
            }
            Mouse.OverrideCursor = _previousCursor;
        }
 
    }
}
