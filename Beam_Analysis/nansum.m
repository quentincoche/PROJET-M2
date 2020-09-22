function [y,idx] = nansum(x, dim)

%NANMEAN Mean of elements ignoring NaNs.
%
%   For vectors, NANMEAN(X) is the mean of the elements in X, ignoring NaNs,
%   i.e., MEAN(X(~ISNAN(X))).
%
%   For matrices, NANMEAN(X) is a row vector containing the NANMEAN value of
%   each column.
%
%   In general, NANMEAN(X) is the NANMEAN value of the elements along the
%   first non-singleton dimension of X.
%
%   NANMEAN(X, DIM) is the NANMEAN value along the dimension DIM of X.
%
%   See also MEAN, STD, MIN, MAX, COV.

%   Author:      Peter John Acklam
%   Time-stamp:  2004-09-22 19:12:54 +0200
%   E-mail:      pjacklam@online.no
%   URL:         http://home.online.no/~pjacklam
%
%   Modifié : J. Fade
%   Date : 2011-07-19

   nargsin = nargin;
   error(nargchk(1, 2, nargsin));

   sx = size(x);
   dx = ndims(x);

   % get first non-singleton dimension, or 1 if none found
   if nargsin < 2
      k = find(sx ~= 1);
         if isempty(k)
         dim = 1;
      else
         dim = k(1);
      end
   else
      if any(size(dim) ~= 1) || dim < 1 || dim ~= round(dim)
         error('Dimension must be a scalar positive integer.');
      end
   end

   n = size(x, dim);

   % degenerate case
   if isempty(x)
      sy = sx;
      if dim <= dx
         sy(dim) = 1;
      end
      y = zeros(sy);
      return;
   end

   % replace NaNs with zeros
   i = isnan(x);
   x(i) = 0;

   % compute sum along dimension `dim'
   s = sum(x, dim);

   % get number of non-NaN values along dimension `dim'
   %n
   idx=sum(~i,dim);
   %if (idx == sum(~i, dim))
       s(idx == 0) = NaN;
   %else
   %   s(idx == 0) = 1;
 
   y = s;
  % end