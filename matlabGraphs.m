clear all;
close all;

trainError = [.32283,.311399,.306264,.303101,.302493, .300283, .298604, 0, 0, 0];
testError = [.307216,.292962,.283399,.280675,277950,.277128,.277418,0,0,0];

varianceInfo = xlsread('players_riskiness2015.csv');