-- copied from https://williamyaoh.com/posts/2020-07-19-deriving-reader-monad.html

import Data.Char as Char

data Reader cfg a = Reader { runReader :: cfg -> a }

instance Functor (Reader cfg) where
  fmap f (Reader cfgF) = Reader (fmap f cfgF)

instance Applicative (Reader cfg) where
  pure x = Reader (const x)
  (<*>) (Reader cfgF) (Reader cfgX) = Reader (\cfg ->
    cfgF cfg (cfgX cfg))

instance Monad (Reader cfg) where
  return = pure
  (>>=) (Reader cfgX) nextFn = Reader (\cfg ->
    runReader (nextFn (cfgX cfg)) cfg)


data ABConfig = ABConfig
  { don'tUseLetterE :: Bool
  , don'tUseLetterL :: Bool
  }


toUpperStr :: String -> Reader ABConfig String
toUpperStr str = Reader (\cfg ->
  let filters :: [Char -> Bool]
      filters = [ if don'tUseLetterE cfg then (/= 'E') else const True
                , if don'tUseLetterL cfg then (/= 'L') else const True
                ]
      passesFilters :: Char -> Bool
      passesFilters c = all (\f -> f c) filters
  in filter passesFilters (fmap Char.toUpper str))


-- welcomeMessage :: String -> String -> Reader ABConfig String
-- welcomeMessage motd username =
--     toUpperStr motd >>= (\upperMOTD ->
--         toUpperStr username >>= (\upperUsername ->
--             -- this was originally `\_ ->`, but i want to show
--             -- that every Reader monad can have the same type.
--             Reader (\cfg ->
--                 "Welcome, " ++
--                 upperUsername ++
--                 "! Message of the day: " ++
--                 upperMOTD)))
-- welcomeMessage :: String -> String -> Reader ABConfig String
-- welcomeMessage motd username =
--     toUpperStr motd >>= (\upperMOTD ->
--         toUpperStr username >>= (\upperUsername ->
--             -- this was originally `\_ ->`, but i want to show
--             -- that every Reader monad can have the same type.
--             Reader (\cfg ->
--                 "Welcome, " ++
--                 upperUsername ++
--                 "! Message of the day: " ++
--                 upperMOTD)))


-- welcomeMessage :: String -> String -> Reader ABConfig String
-- welcomeMessage motd username =
--     toUpperStr motd >>= (\upperMOTD ->
--         toUpperStr username >>= (\upperUsername ->
--             -- this was originally `\_ ->`, but i want to show
--             -- that every Reader monad can have the same type.
--             -- additionally, the point here is that the return
--             -- monad has a function which itself does not use the
--             -- cfg, but which itself is composed of functions that
--             -- do
--             Reader (\cfg ->
--                 "Welcome, " ++
--                 upperUsername ++
--                 "! Message of the day: " ++
--                 upperMOTD)))


welcomeMessage :: String -> String -> Reader ABConfig String
welcomeMessage motd username = do
    upperMOTD <- toUpperStr motd
    upperUsername <- toUpperStr username
    Reader (\cfg -> "Welcome, " ++ upperUsername ++ "! Message of the day: " ++ upperMOTD)


data TwoLetter = TwoLetter
  { first :: String, second :: String }

main = do
    let cfg = ABConfig True False
    let r = toUpperStr "Cheese"
    let result = runReader r $ cfg
    print result

    let r = welcomeMessage "another terrible day" "ahmed biryani"
    print $ runReader r $ cfg

    let cfg = TwoLetter "Y" "T"
    let r = Reader (\cfg -> "hello " ++ (first cfg)) :: Reader TwoLetter String

    let rr = r >>= (\x -> Reader (\cfg -> x ++ (second cfg))) :: Reader TwoLetter String
    let rr_count = r >>= (\x -> Reader (\cfg -> length $ x ++ (second cfg))) :: Reader TwoLetter Int    
    let rr2 = Reader (\cfg -> (runReader r $ cfg) ++ (second cfg)) :: Reader TwoLetter String
    print $ runReader rr $ cfg
    print $ runReader rr2 $ cfg
    print $ runReader rr_count $ cfg
    print 1
