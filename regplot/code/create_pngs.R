options(stringsAsFactors=FALSE)

library(parallel)
# near-collinearity
# outliers
# ceiling effects
# biased residuals
# normal (none)

# formula will be y ~ x1 + x2 + ctl1 + ctrl2 + ... + ctln

gen_data <- function(n, n_predictors, n_controls, messup=NULL){
  stopifnot(n_predictors %in% 2:4,
            n_controls %in% 2:4,
            n < 20000, n > 100,
            messup %in% c('outlier',
                          'ceiling',
                          'biased',
                          'none'))
  
  x <- vector('list', n_predictors)
  b <- vector('list', n_controls)
  
  names_b <- paste0('b', seq(n_controls))
  names_x <- paste0('x', seq(n_predictors))
  
  names(b) <- names_b
  names(x) <- names_x
  
  for (i in seq(n_controls)){
    b[[i]] <- rbinom(n, 1, prob=runif(1, .2, .8))
  }
    
  for (i in seq(n_predictors)){
    x[[i]] <- rnorm(n) * (b[[sample.int(n_controls, size=1)]]+1)*runif(1, .1, 1)
  }

  x0 <- Reduce(`+`, x) 
  b0 <- Reduce(`*`, b)
  
  y0 <- x0 + b0 + x0*b0
  
  ysd <- sd(y0)
  
  if (messup != 'biased'){
    y <- y0 + rnorm(n, mean=0, sd=ysd) 
  } else {
    y <- y0 + rlnorm(n, pmax(1, log(y0), na.rm=TRUE))
  }
  
  y <- y - min(y) + 1
  df <- data.frame(y, x, b)
  
  if (messup == 'outlier') {
    indx <- sample.int(n, 3)
    df[indx, 'y'] <- abs(df[indx, 'y'])+1 * (ysd*8)
  }
  
  if (messup == 'ceiling'){
    trunc_pos <- quantile(y, probs=.92)
    df[df$y > trunc_pos, 'y'] <- trunc_pos
  }

  return(df)
}

plot_lm <- function(fit, outfile){
  png(filename=outfile)
  plot(fit, which=1)
  dev.off()
}

parms_to_plot <- function(n, n_predictors, n_controls, messup, outfile){
  dat <- gen_data(n=n, 
                  n_predictors = n_predictors, 
                  n_controls = n_controls, 
                  messup=messup)
  fit <- lm(y ~ ., data = dat)
  plot_lm(fit, outfile)
}

make_ctrl_df <- function(n, type, outpath){
  df <- data.frame(type         = type,
             id           = sprintf('%07d', 1:n),
             n            = ceiling(runif(n, 100, 10000)),
             n_predictors = sample(2:4, size=n, replace=TRUE),
             n_controls   = sample(2:4, size=n, replace=TRUE))
  df$filename <- file.path(outpath, paste0(type, '_', df$id, '.png'))
  df
}

### create dataframe with training info:
outpath <- 'data/png'
ctrl_df <- rbind(
  make_ctrl_df(30000, type='none', outpath=outpath),
  make_ctrl_df(10000, type='biased', outpath=outpath),
  make_ctrl_df(10000, type='outlier', outpath=outpath),
  make_ctrl_df(10000, type='ceiling', outpath=outpath)
)

write.csv(ctrl_df, file = 'data/control_file.csv', row.names=FALSE)

res <- mcmapply(
  FUN = parms_to_plot,
  n = ctrl_df$n,
  n_predictors = ctrl_df$n_predictors,
  n_controls = ctrl_df$n_controls,
  messup = ctrl_df$type,
  outfile = ctrl_df$filename,
  mc.cores=3,
  mc.preschedule=TRUE
)



