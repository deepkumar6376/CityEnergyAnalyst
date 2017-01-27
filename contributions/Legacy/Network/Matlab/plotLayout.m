%-----------------
% Florian Mueller
% December 2014
%-----------------

function plotLayout(ld,figDir,figName)
    close all;
    set(0,'defaulttextinterpreter','none');

    adj = sparse(double(ld.c.sSpp_e(:,1)),double(ld.c.sSpp_e(:,2)),1);
    addpath('FlorianAux/graphViz4Matlab');
    graphViz4Matlab('-adjMat',adj,'-nodeColors',[1 1 1]);
    rmpath('FlorianAux/graphViz4Matlab');
    
    addpath('FlorianAux/laprint');
    storeSinglePlotLaprint(gcf,figDir,figName,16,[],[]);
    rmpath('FlorianAux/laprint');
end