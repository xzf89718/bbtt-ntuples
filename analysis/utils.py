import ROOT as R
import os
from math import sqrt
R.gROOT.SetStyle("ATLAS")
R.gStyle.SetErrorX(0.5)


def fakerates(pasid, total, trigger, prong):
    data_fakerate = None
    mc_fakerate = None

    p_sig = pasid.ttbarFake.Clone()
    p_bkg = pasid.ttbarTrue.Clone()
    p_bkg.Add(pasid.others.Clone())
    p_data = pasid.data.Clone()

    t_sig = total.ttbarFake.Clone()
    t_bkg = total.ttbarTrue.Clone()
    t_bkg.Add(total.others.Clone())
    t_data = total.data.Clone()

    # ttbar in variable name -> fake-tau ttbar
    p_data_ttbar = p_data.Clone()
    p_data_ttbar.Add(p_bkg, -1.0)
    t_data_ttbar = t_data.Clone()
    t_data_ttbar.Add(t_bkg, -1.0)

    for i in range(0, p_data_ttbar.GetNbinsX() + 2):
        print(f"> bin {i}: num / den -> {p_data_ttbar.GetBinContent(i)} / {t_data_ttbar.GetBinContent(i)}")
        if p_data_ttbar.GetBinContent(i) <= 0:
            print(f"{TermColor.WARNING}data-driven: the {i} bin in numerator <= 0, set it to 0{TermColor.ENDC}")
            p_data_ttbar.SetBinContent(i, 0)
        if t_data_ttbar.GetBinContent(i) <= 0:
            print(f"{TermColor.WARNING}data-driven: the {i} bin in denominator <= 0, set it to 0{TermColor.ENDC}")
            t_data_ttbar.SetBinContent(i, 0)
        
    if R.TEfficiency.CheckConsistency(p_data_ttbar, t_data_ttbar):
        data_fakerate = R.TEfficiency(p_data_ttbar, t_data_ttbar)
        data_fakerate.SetName(f"fakerate_data_trig{trigger}_{prong}")
        data_fakerate.SetStatisticOption(R.TEfficiency.kBUniform)

    # ttbar in variable name -> fake-tau ttbar
    p_mc_ttbar = p_sig
    t_mc_ttbar = t_sig

    for i in range(0, p_mc_ttbar.GetNbinsX() + 2):
        print(f"> bin {i}: num / den -> {p_mc_ttbar.GetBinContent(i)} / {t_mc_ttbar.GetBinContent(i)}")
        if p_mc_ttbar.GetBinContent(i) <= 0:
            print(f"{TermColor.WARNING}mc-driven: the {i} bin in numerator <= 0, set it to 0{TermColor.ENDC}")
            p_mc_ttbar.SetBinContent(i, 0)
        if t_mc_ttbar.GetBinContent(i) <= 0:
            print(f"{TermColor.WARNING}mc-driven: the {i} bin in denominator <= 0, set it to 0{TermColor.ENDC}")
            t_mc_ttbar.SetBinContent(i, 0)

    if R.TEfficiency.CheckConsistency(p_mc_ttbar, t_mc_ttbar):
        mc_fakerate = R.TEfficiency(p_mc_ttbar, t_mc_ttbar)
        mc_fakerate.SetName(f"fakerate_mc_trig{trigger}_{prong}")
        mc_fakerate.SetStatisticOption(R.TEfficiency.kBUniform)

    if not data_fakerate or not mc_fakerate:
        raise ValueError("Not able to get the efficiency!")

    return data_fakerate, mc_fakerate


def reweight1D(plot, varTeX, fileName, suffix, drawOpt="E1"):
    print(f"{TermColor.OKBLUE}~ Reweighitng using <{varTeX}>{TermColor.ENDC}")
    c = R.TCanvas("c", "", 900, 900)
    c.SetRightMargin(1.6 * c.GetRightMargin())
    # templates
    data = plot.data
    ttbar = plot.ttbarFake.Clone()
    ttbar.Add(plot.ttbarTrue)
    others = plot.others

    ratio = data.Clone()
    ratio.Add(others, -1.0)
    mc_ttbar = ttbar

    ratio.Divide(mc_ttbar)
    ratio.SetName(f"Rw1DHist{suffix}")
    ratio.GetXaxis().SetTitle(varTeX)
    ratio.GetXaxis().SetTitleSize(0.045)
    ratio.GetXaxis().SetLabelSize(0.04)
    ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().SetLabelSize(0.04)
    ratio.GetYaxis().SetTitleSize(0.045)
    #expr = "[0]+exp([1]+[2]*x)"
    #expr = "-1*[0]*(TMath::Log10(x+[1]))+[2]"
    expr = "[0]+[1]/(1+x)+[2]/(1+exp([3]+[4]*x))"
    f = R.TF1(f"Rw1DFunc{suffix}", expr, ratio.GetXaxis().GetXmin(),
              ratio.GetXaxis().GetXmax(), 4)
    rtf = R.TFile(
        f"{os.getcwd()}/rootfiles/func{suffix}.root", "recreate")
    #ratio.Fit(f)
    f.SetLineColor(R.kRed - 2)

    ratio.Draw(drawOpt)
    #f.Draw("SAME")

    rtf.cd()
    #f.Write()
    ratio.Write()
    rtf.Close()

    # Add ATLAS label
    text = R.TLatex()
    text.SetNDC()
    text.SetTextFont(72)
    text.SetTextSize(0.045)
    text.DrawLatex(0.51, 0.86, "ATLAS")
    text.SetTextFont(42)
    text.DrawLatex(0.51 + 0.16, 0.86, "Internal")
    text.SetTextSize(0.040)
    text.DrawLatex(0.51, 0.80, "#sqrt{s} = 13 TeV, 139 fb^{-1}")
    # text.SetTextSize(0.035)
    # fit_result = "#Chi^{2} / NDF = " + \
    #     "{:.3f} / {}".format(f.GetChisquare(), (ratio.GetNbinsX() - 1))
    # text.DrawLatex(0.51, 0.74, fit_result)

    c.Update()
    c.SaveAs(fileName)

    return True


def reweightTrue1D(plot, varTeX, fileName, suffix):
    c = R.TCanvas("c", "", 900, 900)
    c.SetRightMargin(1.6 * c.GetRightMargin())
    # templates
    data = plot.data
    ttbarTrue = plot.ttbarTrue
    ttbarFake = plot.ttbarFake
    others = plot.others

    ratio = data.Clone()
    ratio.Add(others, -1.0)
    ratio.Add(ttbarFake, -1.0)
    mc_ttbar = ttbarTrue

    ratio.Divide(mc_ttbar)
    ratio.SetName(f"Rw1DHist{suffix}")
    ratio.GetXaxis().SetTitle(varTeX)
    ratio.GetXaxis().SetTitleSize(0.045)
    ratio.GetXaxis().SetLabelSize(0.04)
    ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().SetLabelSize(0.04)
    ratio.GetYaxis().SetTitleSize(0.045)
    #expr = "[0]+exp([1]+[2]*x)"
    #expr = "-1*[0]*(TMath::Log10(x+[1]))+[2]"
    expr = "[0]+[1]/(1+x)+[2]/(1+exp([3]+[4]*x))"
    f = R.TF1(f"Rw1DFunc{suffix}", expr, ratio.GetXaxis().GetXmin(),
              ratio.GetXaxis().GetXmax(), 4)
    rtf = R.TFile(
        f"{os.getcwd()}/rootfiles/func{suffix}.root", "recreate")
    ratio.Fit(f)
    f.SetLineColor(R.kRed - 2)

    ratio.Draw("E1")
    f.Draw("SAME")

    rtf.cd()
    f.Write()
    ratio.Write()
    rtf.Close()

    # Add ATLAS label
    text = R.TLatex()
    text.SetNDC()
    text.SetTextFont(72)
    text.SetTextSize(0.045)
    text.DrawLatex(0.51, 0.86, "ATLAS")
    text.SetTextFont(42)
    text.DrawLatex(0.51 + 0.16, 0.86, "Internal")
    text.SetTextSize(0.040)
    text.DrawLatex(0.51, 0.80, "#sqrt{s} = 13 TeV, 139 fb^{-1}")
    text.SetTextSize(0.035)
    fit_result = "#Chi^{2} / NDF = " + \
        "{:.3f} / {}".format(f.GetChisquare(), (ratio.GetNbinsX() - 1))
    text.DrawLatex(0.51, 0.74, fit_result)

    c.Update()
    c.SaveAs(fileName)

    return True


def drawStack(plot, varTeX, regionTeX, fileName, systs=None):
    """
    systs = {"systname": (plot_up, plot_down), ...}
    """
    c = R.TCanvas("c", "", 900, 900)
    c.SetRightMargin(1.6 * c.GetRightMargin())
    pad = R.TPad("upper_pad", "", 0, 0.35, 1, 1)
    pad.SetRightMargin(1.6 * pad.GetRightMargin())
    pad.SetBottomMargin(0.03)
    pad.SetTickx(False)
    pad.SetTicky(False)
    pad.Draw()
    ratio = R.TPad("lower_pad", "", 0, 0, 1, 0.35)
    ratio.SetRightMargin(1.6 * ratio.GetRightMargin())
    ratio.SetTopMargin(0)
    ratio.SetBottomMargin(0.4)
    ratio.SetGridy()
    ratio.Draw()

    pad.cd()

    # Always have data
    data = plot.data
    ttbarTrue = plot.ttbarTrue
    ttbarFake = plot.ttbarFake
    stack = R.THStack()
    ttbar = plot.ttbarTrue.Clone("ttbar")
    ttbar.Add(plot.ttbarFake)
    others = plot.others
    # Draw stack with MC contributions
    for h, color in plot.bkgColors():
        h.SetLineWidth(1)
        h.SetLineColor(1)
        h.SetFillColor(R.TColor.GetColor(*color))
        stack.Add(h)
    bkg = stack.GetStack().Last().Clone()
    stack.Draw("HIST")
    stack.GetXaxis().SetLabelSize(0)
    stack.GetXaxis().SetTitleSize(0)
    stack.GetXaxis().SetTitleOffset(1.3)
    stack.GetYaxis().SetTitle("Events")
    stack.GetYaxis().SetLabelSize(0.04)
    stack.GetYaxis().SetTitleSize(0.045)
    stack.SetMaximum(data.GetMaximum() * 1.4)
    stack.GetYaxis().ChangeLabel(1, -1, 0)

    # bkg.SetFillStyle(3254)
    # bkg.SetFillColor(R.kGray + 3)
    # bkg.SetMarkerSize(0)
    # bkg.SetName("Unc.")
    # bkg.Draw("E4 SAME")

    # Draw data
    data.SetMarkerStyle(20)
    data.SetMarkerSize(1.2)
    data.SetLineWidth(2)
    data.SetLineColor(R.kBlack)
    data.Draw("E1 SAME")

    # Add legend
    legend = R.TLegend(0.69, 0.65, 0.90, 0.92)
    legend.SetTextFont(42)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.04)
    legend.SetTextAlign(32)
    legend.AddEntry(data, "Data", "lep")
    legend.AddEntry(ttbarTrue, "ttbar true-#tau", "f")
    legend.AddEntry(ttbarFake, "ttbar fake-#tau", "f")
    legend.AddEntry(others, "others", "f")
    legend.Draw("SAME")

    # Add ATLAS label
    text = R.TLatex()
    text.SetNDC()
    text.SetTextFont(72)
    text.SetTextSize(0.055)
    text.DrawLatex(0.20, 0.86, "ATLAS")
    text.SetTextFont(42)
    text.DrawLatex(0.20 + 0.12, 0.86, "Internal")
    text.SetTextSize(0.045)
    text.DrawLatex(0.20, 0.80, "#sqrt{s} = 13 TeV, 139 fb^{-1}")
    text.SetTextSize(0.040)
    text.DrawLatex(0.20, 0.74, regionTeX)

    ratio.cd()

    resize = 0.65 / 0.35

    err = bkg.Clone()
    err.Divide(bkg)
    err.SetFillStyle(1001)
    err.SetFillColor(R.TColor.GetColor(133, 173, 173))
    err.SetMarkerSize(0)
    err.SetName("Unc.")
    err.GetXaxis().SetTitle(varTeX)
    err.GetXaxis().SetTitleOffset(0.8 * resize)
    err.GetXaxis().SetTitleSize(0.045 * resize)
    err.GetXaxis().SetLabelSize(0.04 * resize)
    err.GetYaxis().SetTitle("Data / Pred.")
    err.GetYaxis().SetTitleOffset(0.4 * resize)
    err.GetYaxis().SetTitleSize(0.045 * resize)
    err.GetYaxis().SetLabelSize(0.04 * resize)
    err.GetYaxis().SetNdivisions(505)
    err.SetMinimum(0.62)
    err.SetMaximum(1.38)
    err.Draw("E2")
    rat = data.Clone()
    rat.Divide(bkg)
    rat.SetTitle("ratio")
    rat.Draw("E1 SAME")

    if systs:
        # so far only ttbar systematics 
        sys_up = data.Clone("sys_up")
        sys_up.SetLineColor(R.TColor.GetColor(189, 27, 108))
        sys_up.SetLineStyle(1)
        sys_up.SetLineWidth(2)
        sys_do = sys_up.Clone("sys_down")
        tot_up = [err.GetBinError(i)**2 for i in range(0, sys_up.GetNbinsX() + 2)]
        tot_do = [err.GetBinError(i)**2 for i in range(0, sys_up.GetNbinsX() + 2)]
        for sn, up_down in systs.items():
            up, do = up_down
            ttbar_up = up.ttbarTrue.Clone("ttbar_up")
            ttbar_up.Add(up.ttbarFake)
            ttbar_do = do.ttbarTrue.Clone("ttbar_down")
            ttbar_do.Add(do.ttbarFake)
            
            # ratio
            ttbar_up.Add(ttbar, -1)
            ttbar_do.Add(ttbar, -1)
            
            for i in range(0, sys_up.GetNbinsX() + 2):
                if bkg.GetBinContent(i) > 0:
                    tot_up[i] += (ttbar_up.GetBinContent(i) / bkg.GetBinContent(i))**2
                    tot_do[i] += (ttbar_do.GetBinContent(i) / bkg.GetBinContent(i))**2
        
        for i in range(0, sys_up.GetNbinsX() + 2):
            sys_up.SetBinContent(i, 1 + sqrt(tot_up[i]))
            sys_do.SetBinContent(i, 1 - sqrt(tot_do[i]))
            sys_up.SetBinError(i, 0)
            sys_do.SetBinError(i, 0)
            
        # plot stat + syst
        sys_up.Draw("HIST SAME")
        sys_do.Draw("HIST SAME")

    # Save the plot
    c.Update()
    c.SaveAs(fileName)
    print(f"{TermColor.OKGREEN}√ {fileName} printed {TermColor.ENDC}")

class TermColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
