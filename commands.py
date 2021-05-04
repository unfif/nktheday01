# %%
if __name__ == '__main__':
    from nkdayscraper.models import engine, Base, Racecourses, create_tables, drop_tables, drop_race_tables
    from sys import argv

    def recreate_racecourses():
        Base.metadata.drop_all(engine, tables=[Racecourses.__table__])
        Base.metadata.create_all(engine, tables=[Racecourses.__table__])

        rc_list = [
            Racecourses(id='01', name='札幌'),
            Racecourses(id='02', name='函館'),
            Racecourses(id='03', name='福島'),
            Racecourses(id='04', name='新潟'),
            Racecourses(id='05', name='東京'),
            Racecourses(id='06', name='中山'),
            Racecourses(id='07', name='中京'),
            Racecourses(id='08', name='京都'),
            Racecourses(id='09', name='阪神'),
            Racecourses(id='10', name='小倉')
        ]

        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine, future=True)

        with Session() as session:
            try:
                session.add_all(rc_list)
                session.commit()
            except:
                session.rollback()
                raise

    def check_records():
        from nkdayscraper.models import Race, HorseResult
        from sqlalchemy.orm import Session

        query = getQueryForDatesOfExistsRecords()\
        .filter(HorseResult.passageratelist == None)\
        .order_by(Race.date.desc())

        print(query.compile(compile_kwargs={"literal_binds": True}))

        with Session(engine) as session:
            result = session.execute(query)

        print('----------------------------[ incomplete_records ]----------------------------')
        for row in result.fetchall():
            print(row[0].strftime('%Y-%m-%d'))

        print('------------------------------------------------------------------------------')

    def exists_records():
        from nkdayscraper.models import Race, HorseResult
        from sqlalchemy.orm import Session

        query = getQueryForDatesOfExistsRecords()\
        .order_by(Race.date.desc())

        print(query.compile(compile_kwargs={"literal_binds": True}))

        with Session(engine) as session:
            result = session.execute(query)

        print('------------------------------[ exists_records ]------------------------------')
        for row in result.fetchall():
            print(row[0].strftime('%Y-%m-%d'))

        print('------------------------------------------------------------------------------')

    def getQueryForDatesOfExistsRecords():
        from sqlalchemy.future import select
        from nkdayscraper.models import Race, HorseResult
        query = select(Race.date.distinct()).join(HorseResult)\
        .filter(HorseResult.margin.notin_((('除外', '中止', '取消'))))
        return query

    if argv[1] == 'help':
        print('-------------------------------[ command_list ]-------------------------------')
        print('create_tables: this command creates all tables in model.')
        print('drop_tables: this command drops some tables.')
        print('drop_race_tables: this command drops tables related race.')
        print('recreate_racecourses: this command drops and creates Racecourses table.')
        print('check_records: this command checks incomplate records and displays race date.')
        print('exists_records: this command checks exists records and displays race date.')
        print('------------------------------------------------------------------------------')
    elif argv[1] == 'create_tables':
        create_tables(engine)
    elif argv[1] == 'drop_tables':
        drop_tables(engine)
    elif argv[1] == 'drop_race_tables':
        drop_race_tables(engine)
    elif argv[1] == 'recreate_racecourses':
        recreate_racecourses()
    elif argv[1] == 'check_records':
        check_records()
    elif argv[1] == 'exists_records':
        exists_records()
    else:
        print(f"'{argv[1]}' is not found in prepared commands.")

    print('done...')

# %%
